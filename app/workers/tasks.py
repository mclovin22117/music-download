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
from app.services.url_parser import URLParser, URLType
from app.utils.downloader import AudioDownloader
from app.config import settings


@celery_app.task(bind=True, name="tasks.download_track")
def download_track_task(self, url: str) -> Dict:
    """
    Download a single track from Spotify or YouTube URL.
    
    Args:
        url: Spotify track URL or YouTube video URL
    
    Returns:
        Dictionary with download result
    """
    try:
        # Identify URL type
        url_type, url_id = URLParser.identify_url(url)
        
        if url_type == URLType.UNKNOWN:
            return {
                "success": False,
                "error": "Unsupported URL type. Please provide a Spotify or YouTube URL.",
                "track": "Unknown"
            }
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Fetching metadata"})
        
        youtube_service = YouTubeService()
        
        # Handle based on URL type
        if url_type == URLType.SPOTIFY_TRACK:
            # Spotify workflow: Get metadata from Spotify, search YouTube
            
            spotify_service = SpotifyService()
            metadata = spotify_service.get_track_metadata(url)
            
            # Update task state
            self.update_state(state="PROGRESS", meta={"step": "Searching YouTube"})
            
            # Search YouTube
            youtube_url = youtube_service.search_track(metadata)
            
            if not youtube_url:
                return {
                    "success": False,
                    "error": "No matching YouTube video found",
                    "track": metadata.title
                }
        
        elif url_type == URLType.YOUTUBE_VIDEO:
            # YouTube workflow: Get metadata directly from YouTube
            youtube_url = url
            metadata = youtube_service.get_video_metadata(youtube_url)
            
            if not metadata:
                return {
                    "success": False,
                    "error": "Failed to extract YouTube video metadata",
                    "track": "Unknown"
                }
        
        else:
            return {
                "success": False,
                "error": f"Invalid URL type for single track download: {url_type}",
                "track": "Unknown"
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
            "file": str(output_file),
            "source": url_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "track": "Unknown"
        }


@celery_app.task(bind=True, name="tasks.download_playlist")
def download_playlist_task(self, url: str) -> Dict:
    """
    Download all tracks from a Spotify or YouTube playlist.
    
    Args:
        url: Spotify playlist URL or YouTube playlist URL
    
    Returns:
        Dictionary with download results
    """
    try:
        # Identify URL type
        url_type, url_id = URLParser.identify_url(url)
        
        if url_type not in [URLType.SPOTIFY_PLAYLIST, URLType.YOUTUBE_PLAYLIST]:
            return {
                "success": False,
                "error": "URL must be a Spotify or YouTube playlist"
            }
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Fetching playlist"})
        
        results = []
        
        if url_type == URLType.SPOTIFY_PLAYLIST:
            # Spotify playlist workflow
            
            spotify_service = SpotifyService()
            tracks = spotify_service.get_playlist_tracks(url)
            
            # Update task state
            self.update_state(
                state="PROGRESS",
                meta={"step": f"Processing {len(tracks)} tracks"}
            )
            
            # Create subtasks for each track
            for track_metadata in tracks:
                # Construct Spotify URL from track ID
                track_url = f"https://open.spotify.com/track/{track_metadata.spotify_id}"
                result = download_track_task.delay(track_url)
                results.append({
                    "task_id": result.id,
                    "track": track_metadata.title,
                    "artist": track_metadata.artist
                })
        
        elif url_type == URLType.YOUTUBE_PLAYLIST:
            # YouTube playlist workflow
            youtube_service = YouTubeService()
            videos = youtube_service.get_playlist_videos(url)
            
            # Update task state
            self.update_state(
                state="PROGRESS",
                meta={"step": f"Processing {len(videos)} videos"}
            )
            
            # Create subtasks for each video
            for video in videos:
                result = download_track_task.delay(video['url'])
                results.append({
                    "task_id": result.id,
                    "track": video['title'],
                    "artist": "YouTube"
                })
        
        return {
            "success": True,
            "total_tracks": len(results),
            "tasks": results,
            "source": url_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
