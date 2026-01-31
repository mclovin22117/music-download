"""
Service for parsing and identifying URL types.
"""
from enum import Enum
from typing import Optional, Tuple
import re


class URLType(str, Enum):
    """Type of URL provided."""
    SPOTIFY_TRACK = "spotify_track"
    SPOTIFY_PLAYLIST = "spotify_playlist"
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_PLAYLIST = "youtube_playlist"
    UNKNOWN = "unknown"


class URLParser:
    """Service for parsing and identifying music URLs."""
    
    @staticmethod
    def identify_url(url: str) -> Tuple[URLType, Optional[str]]:
        """
        Identify the type of URL and extract the ID.
        
        Args:
            url: The URL to identify
        
        Returns:
            Tuple of (URLType, ID or None)
        """
        url = url.strip()
        
        # Spotify URLs
        if "spotify.com" in url or url.startswith("spotify:"):
            if "track" in url:
                track_id = URLParser._extract_spotify_id(url, "track")
                return (URLType.SPOTIFY_TRACK, track_id)
            elif "playlist" in url:
                playlist_id = URLParser._extract_spotify_id(url, "playlist")
                return (URLType.SPOTIFY_PLAYLIST, playlist_id)
        
        # YouTube URLs
        elif "youtube.com" in url or "youtu.be" in url:
            # Check for playlist
            if "list=" in url:
                playlist_id = URLParser._extract_youtube_playlist_id(url)
                return (URLType.YOUTUBE_PLAYLIST, playlist_id)
            # Check for video
            else:
                video_id = URLParser._extract_youtube_video_id(url)
                return (URLType.YOUTUBE_VIDEO, video_id)
        
        return (URLType.UNKNOWN, None)
    
    @staticmethod
    def _extract_spotify_id(url: str, resource_type: str) -> Optional[str]:
        """Extract Spotify ID from URL."""
        # Handle spotify: URIs
        if url.startswith("spotify:"):
            return url.split(":")[-1]
        
        # Handle open.spotify.com URLs
        if "open.spotify.com" in url:
            parts = url.split("/")
            if resource_type in parts:
                idx = parts.index(resource_type)
                spotify_id = parts[idx + 1].split("?")[0]
                return spotify_id
        
        return None
    
    @staticmethod
    def _extract_youtube_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        # Handle youtu.be short URLs
        if "youtu.be/" in url:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
            if match:
                return match.group(1)
        
        # Handle youtube.com URLs
        if "youtube.com" in url:
            # Check for v= parameter
            match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def _extract_youtube_playlist_id(url: str) -> Optional[str]:
        """Extract YouTube playlist ID from URL."""
        match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        return None
    
    @staticmethod
    def is_spotify_url(url: str) -> bool:
        """Check if URL is a Spotify URL."""
        url_type, _ = URLParser.identify_url(url)
        return url_type in [URLType.SPOTIFY_TRACK, URLType.SPOTIFY_PLAYLIST]
    
    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """Check if URL is a YouTube URL."""
        url_type, _ = URLParser.identify_url(url)
        return url_type in [URLType.YOUTUBE_VIDEO, URLType.YOUTUBE_PLAYLIST]
