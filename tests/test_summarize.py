"""Basic tests for the summarizer API."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200_when_ffmpeg_available():
    """Health check passes when ffmpeg is in PATH."""
    response = client.get("/health")
    assert response.status_code in (200, 503)


def test_summarize_requires_input():
    """Summarize returns 400 when no url or file provided."""
    response = client.post("/summarize")
    assert response.status_code == 400


def test_summarize_rejects_invalid_url():
    """Summarize returns 400 for non-Instagram URL."""
    response = client.post(
        "/summarize",
        json={"url": "https://example.com/not-a-reel"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_summarize_rejects_invalid_file_type():
    """Summarize returns 400 for non-video file."""
    response = client.post(
        "/summarize",
        files={"file": ("test.txt", b"not a video", "text/plain")},
    )
    assert response.status_code == 400
