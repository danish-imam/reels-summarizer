import logging
import os
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.logging_config import configure_logging
from app.pipeline import (
    extract_audio,
    fetch_video_from_url,
    summarize_transcript,
    transcribe_audio,
)
from app.schemas import SummarizeResponse

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Reels Summarizer API", version="1.0.0")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}


@app.get("/health")
async def health():
    """Check readiness: ffmpeg available."""
    logger.debug("Health check requested")
    if not shutil.which("ffmpeg"):
        logger.warning("Health check failed: ffmpeg not found")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "issues": ["ffmpeg not found in PATH"]},
        )
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: Request):
    """Transcribe and summarize by Reels URL or file upload. 100% free - no API key needed."""
    video_path = None
    temp_dir = None

    try:
        content_type = request.headers.get("content-type", "")
        logger.info("Summarize request received (content_type=%s)", content_type[:50] if content_type else "none")

        # Option A: URL (JSON body)
        if "application/json" in content_type:
            try:
                body = await request.json()
            except Exception:
                logger.warning("Invalid JSON body in summarize request")
                raise HTTPException(400, "Invalid JSON body")
            url = body.get("url") if body else None
            if not url:
                logger.warning("Summarize request missing 'url' in JSON body")
                raise HTTPException(400, "Provide 'url' in JSON body")
            logger.info("Downloading reel from URL: %s", url)
            video_path = fetch_video_from_url(url)
            temp_dir = str(Path(video_path).parent)
            logger.info("Reel downloaded successfully (path=%s, size=%.2f MB)", video_path, os.path.getsize(video_path) / (1024 * 1024))

        # Option B: File upload (multipart)
        elif "multipart" in content_type:
            form = await request.form()
            file = form.get("file")
            if not file or not hasattr(file, "filename") or not file.filename:
                raise HTTPException(400, "Provide 'file' in multipart form")
            ext = Path(file.filename).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    400,
                    f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
                )
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(400, "File too large (max 50 MB)")
            fd, video_path = tempfile.mkstemp(suffix=ext)
            os.close(fd)
            with open(video_path, "wb") as f:
                f.write(content)
            logger.info("File uploaded: %s (%d bytes)", file.filename, len(content))

        else:
            raise HTTPException(
                400,
                "Provide 'url' in JSON body (Content-Type: application/json) or 'file' in multipart form",
            )

        audio_path = None
        try:
            logger.debug("Extracting audio from video")
            audio_path = extract_audio(video_path)
            logger.info("Transcribing audio with Whisper")
            transcript, duration = transcribe_audio(audio_path)
            logger.debug("Transcription complete (duration_sec=%s, transcript_len=%d)", duration, len(transcript))

            if not transcript:
                transcript = "[No speech detected]"
                summary = "This reel contains no discernible speech to summarize."
            else:
                logger.debug("Summarizing transcript")
                summary = summarize_transcript(transcript)

            logger.info("Summarize completed (transcript=%d words, summary=%d words)", len(transcript.split()), len(summary.split()))
            return SummarizeResponse(
                summary=summary,
                transcript=transcript,
                duration_seconds=duration,
            )
        finally:
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)
                logger.debug("Cleaned up temporary audio file")

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Summarize validation error: %s", e)
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.exception("Summarize failed: %s", e)
        raise HTTPException(500, detail=str(e))
    finally:
        if video_path and os.path.exists(video_path):
            os.unlink(video_path)
            logger.debug("Deleted video file: %s", video_path)
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.debug("Removed temp directory: %s", temp_dir)
