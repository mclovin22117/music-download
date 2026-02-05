"""
Spotify metadata service using web scraping (no API key needed).
"""
import json
from typing import Dict, List
import requests
from bs4 import BeautifulSoup


class SpotifyService:
    """Service for fetching Spotify metadata by scraping web pages."""
    
    def __init__(self):
        """Initialize HTTP session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_track_metadata(self, spotify_url: str) -> Dict[str, str]:
        """
        Get track metadata from Spotify URL by scraping.
        
        Args:
            spotify_url: Spotify track URL
            
        Returns:
            Dictionary with track metadata
        """
        try:
            response = self.session.get(spotify_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract JSON-LD metadata
            script_tag = soup.find('script', {'type': 'application/ld+json'})
            if script_tag:
                data = json.loads(script_tag.string)
                return {
                    "name": data.get('name', 'Unknown'),
                    "artist": data.get('byArtist', {}).get('name', 'Unknown Artist'),
                    "album": data.get('inAlbum', {}).get('name', 'Unknown Album'),
                    "year": data.get('datePublished', '')[:4] if 'datePublished' in data else '',
                    "cover_url": data.get('image', '')
                }
            
            # Fallback: Extract from meta tags
            title = soup.find('meta', {'property': 'og:title'})
            artist = soup.find('meta', {'name': 'music:musician'})
            image = soup.find('meta', {'property': 'og:image'})
            
            name = title['content'] if title else 'Unknown'
            # Parse "Song · Artist" format
            if ' · ' in name:
                name, artist_name = name.split(' · ', 1)
            else:
                artist_name = artist['content'] if artist else 'Unknown Artist'
            
            return {
                "name": name,
                "artist": artist_name,
                "album": "Unknown Album",
                "year": "",
                "cover_url": image['content'] if image else ""
            }
        except Exception as e:
            raise Exception(f"Failed to scrape Spotify metadata: {str(e)}")
    
    def get_playlist_tracks(self, playlist_url: str) -> List[Dict[str, str]]:
        """
        Get all tracks from a Spotify playlist by scraping.
        
        Args:
            playlist_url: Spotify playlist URL
            
        Returns:
            List of track metadata dictionaries
        """
        try:
            response = self.session.get(playlist_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            tracks = []
            
            # Find Spotify embed data in script tags
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'MusicPlaylist':
                        track_list = data.get('track', [])
                        for track in track_list:
                            tracks.append({
                                "name": track.get('name', 'Unknown'),
                                "artist": track.get('byArtist', {}).get('name', 'Unknown Artist'),
                                "album": track.get('inAlbum', {}).get('name', 'Unknown Album'),
                                "year": track.get('datePublished', '')[:4] if 'datePublished' in track else '',
                                "cover_url": track.get('image', '')
                            })
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if not tracks:
                raise ValueError("No tracks found in playlist")
            
            return tracks
        except Exception as e:
            raise Exception(f"Failed to scrape playlist: {str(e)}")
