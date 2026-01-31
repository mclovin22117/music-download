"""
Pydantic models for request/response validation.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field


class TaskStatus(str, Enum):
    """Status of a download task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TrackDownloadRequest(BaseModel):
    """Request model for downloading a single track."""
    url: str = Field(..., description="Spotify track URL or YouTube video URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            }
        }


class PlaylistDownloadRequest(BaseModel):
    """Request model for downloading a playlist."""
    url: str = Field(..., description="Spotify playlist URL or YouTube playlist URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
            }
        }


class TaskResponse(BaseModel):
    """Response model for task creation."""
    task_id: str
    status: TaskStatus
    message: str


class TrackMetadata(BaseModel):
    """Metadata for a single track."""
    title: str
    artist: str
    album: str
    duration_ms: int
    cover_art_url: Optional[str] = None
    spotify_id: str


class TaskStatusResponse(BaseModel):
    """Response model for task status queries."""
    task_id: str
    status: TaskStatus
    result: Optional[dict] = None
    error: Optional[str] = None
