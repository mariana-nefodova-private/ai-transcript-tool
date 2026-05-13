import os
import tempfile
from datetime import timedelta

import ffmpeg
import whisper


def _format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _extract_audio(video_path: str, audio_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, ac=1, ar=16000, acodec="pcm_s16le")
        .overwrite_output()
        .run(quiet=True)
    )


def transcribe(video_path: str, model_name: str = "large-v2", progress_callback=None) -> str:
    def update(pct, msg):
        if progress_callback:
            progress_callback(pct, msg)

    audio_path = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_path = tmp.name
        tmp.close()

        update(5, "Extracting audio from video…")
        _extract_audio(video_path, audio_path)

        update(15, "Loading Whisper AI model…")
        model = whisper.load_model(model_name)

        update(20, "Transcribing… this takes a few minutes for long recordings")
        result = model.transcribe(
            audio_path,
            task="transcribe",
            verbose=False,
            fp16=False,
        )

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
