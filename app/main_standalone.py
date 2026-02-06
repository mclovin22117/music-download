"""
FastAPI application for standalone desktop app (no Redis/Celery).
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio
from pathlib import Path
import os

from app.services.url_parser import URLParser
from app.services.spotify_service import SpotifyService
from app.services.youtube_service import YouTubeService
from app.services.metadata_service import MetadataService
from app.utils.downloader import Downloader

app = FastAPI(
    title="Music Download API (Standalone)",
    version="1.0.0",
    description="Standalone music downloader for desktop app"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Initialize services
url_parser = URLParser()
spotify_service = SpotifyService()
youtube_service = YouTubeService()
metadata_service = MetadataService()
downloader = Downloader()

# In-memory task storage
tasks: Dict[str, Dict] = {}
task_counter = 0

# Download directory
DOWNLOAD_DIR = Path.home() / "Music" / "Music Downloader"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DownloadRequest(BaseModel):
    url: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    track: Optional[str] = None
    artist: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None


def download_track_sync(task_id: str, url: str):
    """Synchronous download function for background task."""
    try:
        tasks[task_id]["status"] = "started"
        
        # Parse URL
        url_info = url_parser.parse_url(url)
        
        if url_info["platform"] == "spotify":
            # Get Spotify metadata
            metadata = spotify_service.get_track_metadata(url)
            tasks[task_id]["track"] = metadata["name"]
            tasks[task_id]["artist"] = metadata["artist"]
            
            # Search on YouTube
            query = f"{metadata['artist']} {metadata['name']}"
            youtube_url = youtube_service.search_track(query)
            
            if not youtube_url:
                raise Exception("Could not find track on YouTube")
            
            url_to_download = youtube_url
        else:
            # Direct YouTube download
            url_to_download = url
            metadata = {}
        
        tasks[task_id]["status"] = "downloading"
        
        # Download
        file_path = downloader.download_audio(url_to_download, str(DOWNLOAD_DIR))
        
        if not file_path:
            raise Exception("Download failed")
        
        # Add metadata if from Spotify
        if metadata:
            metadata_service.add_metadata(file_path, metadata)
        
        # Update task
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["file_path"] = file_path
        
        # Extract track info from file if not already set
        if not tasks[task_id].get("track"):
            filename = Path(file_path).stem
            tasks[task_id]["track"] = filename
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Music Download API (Standalone)",
        "version": "1.0.0",
        "status": "operational",
        "mode": "standalone"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "mode": "standalone"}


@app.post("/api/tracks/download")
async def download_track(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a track download."""
    global task_counter
    
    task_counter += 1
    task_id = f"task_{task_counter}"
    
    # Initialize task
    tasks[task_id] = {
        "status": "pending",
        "track": None,
        "artist": None,
        "file_path": None,
        "error": None
    }
    
    # Add to background tasks
    background_tasks.add_task(download_track_sync, task_id, request.url)
    
    return {"task_id": task_id, "status": "pending"}


@app.get("/api/tracks/status/{task_id}")
async def get_task_status(task_id: str):
    """Get download task status."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]


@app.post("/api/playlists/download")
async def download_playlist(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a playlist download."""
    try:
        url_info = url_parser.parse_url(request.url)
        
        if url_info["platform"] == "spotify" and url_info["type"] == "playlist":
            # Get playlist tracks
            tracks = spotify_service.get_playlist_tracks(request.url)
            
            task_ids = []
            for track in tracks:
                global task_counter
                task_counter += 1
                task_id = f"task_{task_counter}"
                
                # Initialize task
                tasks[task_id] = {
                    "status": "pending",
                    "track": track["name"],
                    "artist": track["artist"],
                    "file_path": None,
                    "error": None
                }
                
                # Queue download
                query = f"{track['artist']} {track['name']}"
                youtube_url = youtube_service.search_track(query)
                
                if youtube_url:
                    background_tasks.add_task(download_track_sync, task_id, youtube_url)
                    task_ids.append({"task_id": task_id, "track": track["name"]})
            
            return {
                "status": "started",
                "total_tracks": len(task_ids),
                "tasks": task_ids
            }
        
        elif url_info["platform"] == "youtube" and url_info["type"] == "playlist":
            # YouTube playlist handling would go here
            raise HTTPException(status_code=501, detail="YouTube playlists not yet implemented")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid playlist URL")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
