import os
import time
import threading
import tempfile
from datetime import timedelta

import ffmpeg
import torch
import whisper


def _format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _extract_audio(video_path: str, audio_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, ac=1, ar=16000, acodec="pcm_s16le")
        .overwrite_output()
        .run(quiet=True)
    )


def _get_device() -> str:
    try:
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            torch.zeros(1, device="mps")  # sanity check
            return "mps"
    except Exception:
        pass
    return "cpu"


def _audio_duration(audio_path: str) -> float:
    try:
        probe = ffmpeg.probe(audio_path)
        for stream in probe["streams"]:
            if stream.get("codec_type") == "audio":
                return float(stream.get("duration", 0))
        return float(probe["format"].get("duration", 0))
    except Exception:
        return 0.0


def transcribe(video_path: str, model_name: str = "medium", progress_callback=None) -> str:
    def update(pct: int, msg: str) -> None:
        if progress_callback:
            progress_callback(pct, msg)

    audio_path = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_path = tmp.name
        tmp.close()

        update(5, "Extracting audio…")
        _extract_audio(video_path, audio_path)

        update(12, "Loading AI model…")
        device = _get_device()
        model = whisper.load_model(model_name, device=device)

        duration = _audio_duration(audio_path)

        # Conservative real-time speed estimates per model+device combo
        # (used only for progress display — does not affect accuracy)
        speed_map = {
            ("medium", "mps"): 2.0,
            ("medium", "cpu"): 7.0,
            ("large-v2", "mps"): 5.0,
            ("large-v2", "cpu"): 18.0,
        }
        speed = speed_map.get((model_name, device), 8.0)
        estimated_seconds = max(duration / speed, 15)

        update(20, "Transcribing… 20%")
        start = time.time()
        running = [True]

        def _ticker():
            while running[0]:
                elapsed = time.time() - start
                frac = min(elapsed / estimated_seconds, 0.98)
                pct = int(20 + frac * 72)   # 20% → 92%
                update(pct, f"Transcribing… {pct}%")
                time.sleep(3)

        ticker = threading.Thread(target=_ticker, daemon=True)
        ticker.start()

        try:
            result = model.transcribe(
                audio_path,
                task="transcribe",
                verbose=False,
                fp16=False,   # fp16=False is stable on both CPU and MPS
            )
        finally:
            running[0] = False
            ticker.join(timeout=5)

        update(95, "Formatting transcript…")
        lines = []
        for segment in result["segments"]:
            text = segment["text"].strip()
            if text:
                ts = _format_timestamp(segment["start"])
                lines.append(f"[{ts}] {text}")

        update(100, "Done!")
        return "\n".join(lines)

    finally:
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
