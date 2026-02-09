import logging
import tempfile
from pathlib import Path

from pydub import AudioSegment

logger = logging.getLogger(__name__)


def extract_audio(video_path: str | Path) -> str:
    """Extract audio from video file to a temporary WAV file."""
    video_path = Path(video_path)
    if not video_path.exists():
        logger.error("Video file not found: %s", video_path)
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.debug("Extracting audio from %s", video_path)
    audio = AudioSegment.from_file(str(video_path))
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    audio.export(temp_path, format="wav")
    logger.debug("Audio extracted to %s (duration=%.1fs)", temp_path, len(audio) / 1000)
    return temp_path
