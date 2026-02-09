import logging
from pathlib import Path

import whisper

logger = logging.getLogger(__name__)


def transcribe_audio(audio_path: str | Path) -> tuple[str, float | None]:
    """Transcribe audio file using local Whisper. Returns (transcript, duration_seconds)."""
    audio_path = Path(audio_path)
    if not audio_path.exists():
        logger.error("Audio file not found: %s", audio_path)
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.debug("Loading Whisper model (base)")
    model = whisper.load_model("base")
    logger.debug("Transcribing audio file: %s", audio_path)
    result = model.transcribe(str(audio_path))

    transcript = result.get("text", "").strip()
    duration = None
    if "segments" in result and result["segments"]:
        last_segment = result["segments"][-1]
        duration = last_segment.get("end")

    logger.debug("Transcription done (duration=%s, transcript_len=%d)", duration, len(transcript))
    return transcript, duration
