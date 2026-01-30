"""
Celery tasks for downloading and processing audio.
"""
from pathlib import Path
from typing import Dict, List
from celery import group

from app.workers.celery_app import celery_app
from app.services.spotify_service import SpotifyService
from app.services.youtube_service import YouTubeService
from app.services.metadata_service import MetadataService
from app.utils.downloader import AudioDownloader
from app.config import settings


@celery_app.task(bind=True, name="tasks.download_track")
def download_track_task(self, spotify_url: str) -> Dict:
    """
    Download a single track.
    
    Args:
        spotify_url: Spotify track URL
    
    Returns:
        Dictionary with download result
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Fetching metadata"})
        
        # Fetch Spotify metadata
        spotify_service = SpotifyService()
        metadata = spotify_service.get_track_metadata(spotify_url)
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Searching YouTube"})
        
        # Search YouTube
        youtube_service = YouTubeService()
        youtube_url = youtube_service.search_track(metadata)
        
        if not youtube_url:
            return {
                "success": False,
                "error": "No matching YouTube video found",
                "track": metadata.title
            }
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Downloading audio"})
        
        # Download audio
        downloader = AudioDownloader(settings.download_dir)
        output_file = downloader.download(youtube_url, metadata)
        
        if not output_file:
            return {
                "success": False,
                "error": "Failed to download audio",
                "track": metadata.title
            }
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Embedding metadata"})
        
        # Embed metadata
        metadata_service = MetadataService()
        metadata_service.embed_metadata(output_file, metadata)
        
        return {
            "success": True,
            "track": metadata.title,
            "artist": metadata.artist,
            "file": str(output_file)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "track": "Unknown"
        }


@celery_app.task(bind=True, name="tasks.download_playlist")
def download_playlist_task(self, spotify_url: str) -> Dict:
    """
    Download all tracks from a playlist.
    
    Args:
        spotify_url: Spotify playlist URL
    
    Returns:
        Dictionary with download results
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Fetching playlist"})
        
        # Fetch playlist tracks
        spotify_service = SpotifyService()
        tracks = spotify_service.get_playlist_tracks(spotify_url)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"step": f"Processing {len(tracks)} tracks"}
        )
        
        # Create subtasks for each track
        results = []
        for track_metadata in tracks:
            # For playlists, we need to construct a Spotify URL from the track ID
            track_url = f"https://open.spotify.com/track/{track_metadata.spotify_id}"
            result = download_track_task.delay(track_url)
            results.append({
                "task_id": result.id,
                "track": track_metadata.title,
                "artist": track_metadata.artist
            })
        
        return {
            "success": True,
            "total_tracks": len(tracks),
            "tasks": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
