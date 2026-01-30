"""
Spotify API service for fetching track and playlist metadata.
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Optional

from app.config import settings
from app.models import TrackMetadata


class SpotifyService:
    """Service for interacting with Spotify API."""
    
    def __init__(self):
        """Initialize Spotify client with credentials."""
        auth_manager = SpotifyClientCredentials(
            client_id=settings.spotify_client_id,
            client_secret=settings.spotify_client_secret
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)
    
    def get_track_metadata(self, track_url: str) -> TrackMetadata:
        """
        Fetch metadata for a single track.
        
        Args:
            track_url: Spotify track URL or URI
        
        Returns:
            TrackMetadata object
        """
        # Extract track ID from URL
        track_id = self._extract_id_from_url(track_url, "track")
        
        # Fetch track data
        track = self.client.track(track_id)
        
        return TrackMetadata(
            title=track["name"],
            artist=", ".join([artist["name"] for artist in track["artists"]]),
            album=track["album"]["name"],
            duration_ms=track["duration_ms"],
            cover_art_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            spotify_id=track["id"]
        )
    
    def get_playlist_tracks(self, playlist_url: str) -> List[TrackMetadata]:
        """
        Fetch all tracks from a playlist.
        
        Args:
            playlist_url: Spotify playlist URL or URI
        
        Returns:
            List of TrackMetadata objects
        """
        # Extract playlist ID from URL
        playlist_id = self._extract_id_from_url(playlist_url, "playlist")
        
        tracks = []
        results = self.client.playlist_tracks(playlist_id)
        
        while results:
            for item in results["items"]:
                if item["track"]:  # Some tracks might be None
                    track = item["track"]
                    tracks.append(TrackMetadata(
                        title=track["name"],
                        artist=", ".join([artist["name"] for artist in track["artists"]]),
                        album=track["album"]["name"],
                        duration_ms=track["duration_ms"],
                        cover_art_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                        spotify_id=track["id"]
                    ))
            
            # Check for next page
            if results["next"]:
                results = self.client.next(results)
            else:
                results = None
        
        return tracks
    
    @staticmethod
    def _extract_id_from_url(url: str, resource_type: str) -> str:
        """
        Extract Spotify ID from URL.
        
        Args:
            url: Spotify URL or URI
            resource_type: Type of resource (track, playlist, album)
        
        Returns:
            Spotify ID
        """
        # Handle spotify: URIs
        if url.startswith("spotify:"):
            return url.split(":")[-1]
        
        # Handle open.spotify.com URLs
        if "open.spotify.com" in url:
            parts = url.split("/")
            if resource_type in parts:
                idx = parts.index(resource_type)
                spotify_id = parts[idx + 1].split("?")[0]  # Remove query parameters
                return spotify_id
        
        # Assume it's already an ID
        return url
