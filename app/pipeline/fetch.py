import logging
import os
import re
import tempfile
from pathlib import Path

import certifi
import yt_dlp

from app.config import get_settings

logger = logging.getLogger(__name__)

# Ensure SSL certs are found (fixes macOS Python "certificate verify failed")
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

INSTAGRAM_REEL_PATTERN = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)


def is_instagram_reel_url(url: str) -> bool:
    """Check if URL is a valid Instagram Reel URL."""
    return bool(INSTAGRAM_REEL_PATTERN.match(url.strip()))


def fetch_video_from_url(url: str) -> str:
    """Download video from Instagram Reel URL using yt-dlp. Returns path to temp file."""
    url = url.strip()
    if not is_instagram_reel_url(url):
        logger.warning("Invalid Instagram Reel URL received: %s", url)
        raise ValueError(f"Invalid Instagram Reel URL: {url}")

    temp_dir = tempfile.mkdtemp()
    output_template = str(Path(temp_dir) / "video.%(ext)s")
    logger.debug("Created temp dir for download: %s", temp_dir)

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,  # Workaround for corporate proxy / macOS SSL issues
    }

    settings = get_settings()
    if settings.instagram_cookies:
        cookies_path = Path(settings.instagram_cookies).expanduser()
        if cookies_path.exists():
            ydl_opts["cookiefile"] = str(cookies_path)
            logger.debug("Using cookies file: %s", cookies_path)

    try:
        logger.info("Starting yt-dlp download for: %s", url)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        msg = str(e).split("\n")[0] if e else "Download failed"
        if "login" in msg.lower() or "cookies" in msg.lower() or "private" in msg.lower():
            raise ValueError(
                f"Instagram requires login. Set INSTAGRAM_COOKIES with a cookies file path. Error: {msg}"
            ) from e
        raise ValueError(f"Download failed: {msg}") from e

    for ext in ["mp4", "webm", "mkv"]:
        path = Path(temp_dir) / f"video.{ext}"
        if path.exists():
            logger.info("Downloaded video to %s (%.2f MB)", path, path.stat().st_size / (1024 * 1024))
            return str(path)

    logger.error("yt-dlp completed but no output file found in %s", temp_dir)
    raise RuntimeError("Failed to download video: no output file found")
