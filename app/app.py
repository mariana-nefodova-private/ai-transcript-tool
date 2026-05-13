import os
import sys
import uuid
import threading
import webbrowser
import tempfile

from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(__file__))
from transcriber import transcribe

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 GB

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory job store: job_id -> dict
JOBS: dict[str, dict] = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def start_transcription():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".mp4"):
        return jsonify({"error": "Only MP4 files are supported"}), 400

    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    video_path = os.path.join(UPLOAD_DIR, f"{job_id}_{filename}")
    file.save(video_path)

    JOBS[job_id] = {
        "status": "running",
        "progress": 0,
        "message": "Starting…",
        "transcript": None,
        "filename": filename,
    }

    def run():
        def on_progress(pct, msg):
            JOBS[job_id]["progress"] = pct
            JOBS[job_id]["message"] = msg

        try:
            transcript = transcribe(video_path, progress_callback=on_progress)
            JOBS[job_id]["transcript"] = transcript
            JOBS[job_id]["status"] = "done"
        except Exception as exc:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["message"] = str(exc)
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def job_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
    })


@app.route("/result/<job_id>")
def job_result(job_id):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Not ready"}), 404
    return jsonify({"transcript": job["transcript"]})


@app.route("/download/<job_id>")
def download(job_id):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Not ready"}), 404

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    tmp.write(job["transcript"])
    tmp.close()

    base = os.path.splitext(job["filename"])[0]
    return send_file(
        tmp.name,
        as_attachment=True,
        download_name=f"{base}_transcript.txt",
        mimetype="text/plain; charset=utf-8",
    )


PORT = 7654

if __name__ == "__main__":
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", PORT)) == 0:
            print(f"\n ERROR: Port {PORT} is already in use.")
            print("Close any other running instance of this app and try again.\n")
            raise SystemExit(1)
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(debug=False, port=PORT, threaded=True)
