# Instagram Reels Summarizer API

Transcribe and summarize video files (Reels, etc.). **100% free** – no API keys required.

## How it works

- **Download** (URL only): yt-dlp fetches the Reel to a temp directory (deleted after processing; not persisted)
- **Transcription**: Local Whisper (free)
- **Summarization**: Sumy extractive summarization (free, no API)

## Requirements

- Python 3.11+
- ffmpeg (for audio extraction)

## Setup

```bash
# Install ffmpeg (macOS)
brew install ffmpeg

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

## Usage

**POST /summarize** — By Reels URL or file upload.

```bash
# By Instagram Reel URL (downloads with yt-dlp, then transcribes)
curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/..."}'

# By file upload
curl -X POST http://127.0.0.1:8000/summarize \
  -F "file=@/path/to/video.mp4"
```

Response:

```json
{
  "summary": "Key points from the reel.",
  "transcript": "Full transcript of the audio.",
  "duration_seconds": 12.5
}
```

## Instagram Reels URL: Cookies (often required)

Instagram often blocks unauthenticated downloads. To use the URL option:

1. Install a browser extension to export cookies (e.g. "Get cookies.txt" for Chrome/Firefox)
2. Log into Instagram in your browser, go to instagram.com, export cookies as Netscape format
3. Save to a file (e.g. `instagram_cookies.txt`) and add to `.env`:
   ```
   INSTAGRAM_COOKIES=/path/to/instagram_cookies.txt
   ```

If you get "login required" or 500 errors, try the **file upload** option instead – download the Reel manually (e.g. from a site like instagramdownloader.io) and upload the file.

**Where does the reel go?** Downloaded to a system temp directory (e.g. `/tmp/` or `/var/folders/...`) and automatically deleted after transcription. It is not saved to disk.

## Optional: Better summaries with Gemini

For AI-generated summaries (instead of extractive), add a free [Gemini API key](https://aistudio.google.com/apikey) (no credit card) and uncomment `google-generativeai` in requirements.txt, then add `GEMINI_API_KEY` to your `.env`.
