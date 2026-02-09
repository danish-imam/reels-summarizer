from typing import Optional

from pydantic import BaseModel, Field


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="Summary of the reel content")
    transcript: str = Field(..., description="Full transcript of the audio")
    duration_seconds: Optional[float] = Field(None, description="Duration of the video in seconds")
