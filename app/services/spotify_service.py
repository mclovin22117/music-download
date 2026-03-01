"""
Spotify metadata service using web scraping (no API key needed).
"""
import json
import re
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
            
            # DEBUG: Print the page title
            title_tag = soup.find('title')
            if title_tag:
                print(f"DEBUG - Page title: {title_tag.text}")
            
            # METHOD 1: Try extracting from page title first
            if title_tag:
                # Spotify titles are usually "Song | Artist | Spotify"
                full_title = title_tag.text.strip()
                parts = [p.strip() for p in full_title.split('|')]
                print(f"DEBUG - Title parts: {parts}")
                
                if len(parts) >= 2:
                    track_name = parts[0]
                    artist_name = parts[1]
                    
                    # Clean up track name (remove " - song and lyrics" etc.)
                    track_name = re.sub(r'\s*-\s*(song|track|audio|official|lyrics).*$', '', track_name, flags=re.IGNORECASE)
                    track_name = track_name.strip()
                    
                    # Clean up artist name - don't use if it's "Spotify"
                    if ' - song' in artist_name.lower():
                        artist_name = artist_name.split(' - ')[0].strip()
                    
                    # If artist_name is "Spotify", skip this method
                    if artist_name.lower() != 'spotify':
                        print(f"DEBUG - Extracted from title: {track_name} by {artist_name}")
                        return {
                            "name": track_name,
                            "artist": artist_name,
                            "album": "Unknown Album",
                            "year": "",
                            "cover_url": ""
                        }
            
            # METHOD 2: Extract from meta tags
            og_title = soup.find('meta', {'property': 'og:title'})
            og_description = soup.find('meta', {'property': 'og:description'})
            
            print(f"DEBUG - og:title: {og_title['content'] if og_title else 'Not found'}")
            print(f"DEBUG - og:description: {og_description['content'] if og_description else 'Not found'}")
            
            track_name = 'Unknown'
            artist_name = 'Unknown Artist'
            
            if og_title:
                # og:title is usually "Song · Artist" or just "Song"
                content = og_title['content']
                if ' · ' in content:
                    track_name, artist_name = content.split(' · ', 1)
                elif ' - ' in content:
                    track_name, artist_name = content.split(' - ', 1)
                else:
                    track_name = content
            
            # Try getting artist from description
            if og_description and (artist_name == 'Unknown Artist' or artist_name.lower() == 'spotify'):
                desc = og_description['content']
                # Description format: "Artist · Song · Duration" or "Song by Artist"
                if ' · ' in desc:
                    parts = desc.split(' · ')
                    if len(parts) >= 1:
                        # First part is usually the artist
                        potential_artist = parts[0].strip()
                        if potential_artist.lower() != 'spotify':
                            artist_name = potential_artist
                elif ' by ' in desc.lower():
                    # "Song by Artist" format
                    match = re.search(r'by\s+(.+?)(?:\s+·|\s+\||$)', desc, re.IGNORECASE)
                    if match:
                        artist_name = match.group(1).strip()
            
            print(f"DEBUG - Final extracted: {track_name} by {artist_name}")
            
            return {
                "name": track_name,
                "artist": artist_name,
                "album": "Unknown Album",
                "year": "",
                "cover_url": ""
            }
            
        except Exception as e:
            print(f"DEBUG - Exception: {str(e)}")
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