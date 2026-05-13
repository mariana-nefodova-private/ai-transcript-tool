"""
Standalone transcription worker — run as a subprocess by app.py.
Usage: python worker.py <video_path> <model_name> <progress_file> <result_file>
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcriber import transcribe


def main():
    if len(sys.argv) != 5:
        sys.exit(1)

    video_path, model_name, progress_file, result_file = sys.argv[1:5]

    def on_progress(pct: int, msg: str) -> None:
        try:
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump({"p": pct, "m": msg}, f)
        except Exception:
            pass

    try:
        transcript = transcribe(video_path, model_name, on_progress)
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({"status": "done", "transcript": transcript}, f, ensure_ascii=False)
    except Exception as exc:
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({"status": "error", "message": str(exc)}, f)
    finally:
        try:
            if os.path.exists(video_path):
                os.unlink(video_path)
        except Exception:
            pass


if __name__ == "__main__":
    main()
