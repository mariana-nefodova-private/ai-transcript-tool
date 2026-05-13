import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import webbrowser

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library as lib

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 GB

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

WORKER = os.path.join(os.path.dirname(__file__), "worker.py")

JOBS: dict[str, dict] = {}


# ── UI ────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Transcription ─────────────────────────────────────────────────────────────

@app.route("/transcribe", methods=["POST"])
def start_transcription():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".mp4"):
        return jsonify({"error": "Only MP4 files are supported"}), 400

    model_name = request.form.get("model", "medium")
    if model_name not in ("medium", "large-v2"):
        model_name = "medium"

    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    video_path = os.path.join(UPLOAD_DIR, f"{job_id}_{filename}")
    file.save(video_path)

    progress_file = os.path.join(UPLOAD_DIR, f"{job_id}_progress.json")
    result_file   = os.path.join(UPLOAD_DIR, f"{job_id}_result.json")

    proc = subprocess.Popen(
        [sys.executable, WORKER, video_path, model_name, progress_file, result_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    JOBS[job_id] = {
        "status":        "running",
        "progress":      0,
        "message":       "Starting…",
        "transcript":    None,
        "filename":      filename,
        "process":       proc,
        "progress_file": progress_file,
        "result_file":   result_file,
    }

    def _monitor():
        proc.wait()
        try:
            with open(result_file, encoding="utf-8") as f:
                data = json.load(f)
            if data["status"] == "done":
                JOBS[job_id].update(
                    transcript=data["transcript"],
                    status="done",
                    progress=100,
                    message="Done!",
                )
            else:
                JOBS[job_id].update(status="error", message=data.get("message", "Unknown error"))
        except Exception:
            if JOBS[job_id]["status"] == "running":
                JOBS[job_id].update(status="error", message="Transcription failed")
        finally:
            for path in (progress_file, result_file):
                try:
                    os.unlink(path)
                except Exception:
                    pass

    def _poll_progress():
        while JOBS[job_id]["status"] == "running":
            try:
                with open(progress_file, encoding="utf-8") as f:
                    d = json.load(f)
                JOBS[job_id]["progress"] = d.get("p", 0)
                JOBS[job_id]["message"]  = d.get("m", "Processing…")
            except Exception:
                pass
            time.sleep(1)

    threading.Thread(target=_monitor,       daemon=True).start()
    threading.Thread(target=_poll_progress, daemon=True).start()

    return jsonify({"job_id": job_id})


@app.route("/cancel/<job_id>", methods=["POST"])
def cancel_job(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    proc = job.get("process")
    if proc and proc.poll() is None:
        proc.terminate()
    job.update(status="cancelled", message="Cancelled")
    return jsonify({"ok": True})


@app.route("/status/<job_id>")
def job_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"status": job["status"], "progress": job["progress"], "message": job["message"]})


@app.route("/result/<job_id>")
def job_result(job_id):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Not ready"}), 404
    return jsonify({"transcript": job["transcript"], "filename": job["filename"]})


@app.route("/download/<job_id>")
def download_job(job_id):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Not ready"}), 404
    return _txt_response(job["transcript"], job["filename"])


# ── Library ───────────────────────────────────────────────────────────────────

@app.route("/library")
def get_library():
    return jsonify(lib.get_all())


@app.route("/library/projects", methods=["POST"])
def create_project():
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    return jsonify(lib.create_project(name))


@app.route("/library/projects/<pid>", methods=["PATCH"])
def rename_project(pid):
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    result = lib.rename_project(pid, name)
    return jsonify(result) if result else (jsonify({"error": "Not found"}), 404)


@app.route("/library/projects/<pid>", methods=["DELETE"])
def delete_project(pid):
    return jsonify({"ok": True}) if lib.delete_project(pid) else (jsonify({"error": "Not found"}), 404)


@app.route("/library/transcripts", methods=["POST"])
def save_to_library():
    data       = request.json or {}
    job_id     = data.get("job_id")
    project_id = data.get("project_id") or None
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Job not ready"}), 400
    t = lib.save_transcript(job["filename"], job["transcript"], project_id)
    return jsonify(t)


@app.route("/library/transcripts/<tid>", methods=["DELETE"])
def delete_transcript(tid):
    return jsonify({"ok": True}) if lib.delete_transcript(tid) else (jsonify({"error": "Not found"}), 404)


@app.route("/library/transcripts/<tid>/download")
def download_library_transcript(tid):
    data = lib.get_all()
    t = data["transcripts"].get(tid)
    if not t:
        return jsonify({"error": "Not found"}), 404
    return _txt_response(t["transcript"], t["filename"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _txt_response(text: str, original_filename: str):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.write(text)
    tmp.close()
    base = os.path.splitext(original_filename)[0]
    return send_file(tmp.name, as_attachment=True,
                     download_name=f"{base}_transcript.txt",
                     mimetype="text/plain; charset=utf-8")


# ── Entry point ───────────────────────────────────────────────────────────────

PORT = 7654

if __name__ == "__main__":
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", PORT)) == 0:
            print(f"\n ERROR: Port {PORT} is already in use.")
            print("Close any other running instance and try again.\n")
            raise SystemExit(1)

    def _open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{PORT}")

    threading.Thread(target=_open_browser, daemon=True).start()
    app.run(debug=False, host="0.0.0.0", port=PORT, threaded=True)
