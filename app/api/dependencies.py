"""
FastAPI dependencies.
"""
from app.services.spotify_service import SpotifyService


def get_spotify_service() -> SpotifyService:
    """Dependency for getting Spotify service."""
    return SpotifyService()
