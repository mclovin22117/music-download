"""
YouTube search service for finding matching audio and extracting metadata.
"""
import yt_dlp
from typing import Optional, List, Dict
from app.models import TrackMetadata


class YouTubeService:
    """Service for searching YouTube for matching tracks and extracting metadata."""
    
    def get_video_metadata(self, youtube_url: str) -> Optional[TrackMetadata]:
        """
        Extract metadata from a YouTube video.
        
        Args:
            youtube_url: YouTube video URL
        
        Returns:
            TrackMetadata object or None
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                if not info:
                    return None
                
                # Parse title to extract artist and song name
                title = info.get('title', '')
                artist, song_title = self._parse_title(title)
                
                # Get thumbnail as cover art
                thumbnail = info.get('thumbnail', None)
                
                return TrackMetadata(
                    title=song_title,
                    artist=artist,
                    album=info.get('uploader', 'YouTube'),
                    duration_ms=int(info.get('duration', 0) * 1000),
                    cover_art_url=thumbnail,
                    spotify_id=info.get('id', '')  # Using YouTube ID here
                )
                
        except Exception as e:
            print(f"Error extracting YouTube metadata: {e}")
            return None
    
    def get_playlist_videos(self, playlist_url: str) -> List[Dict]:
        """
        Get all videos from a YouTube playlist.
        
        Args:
            playlist_url: YouTube playlist URL
        
        Returns:
            List of video info dictionaries
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        videos = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if playlist_info and 'entries' in playlist_info:
                    for entry in playlist_info['entries']:
                        if entry:
                            videos.append({
                                'id': entry.get('id'),
                                'title': entry.get('title'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                            })
        
        except Exception as e:
            print(f"Error extracting playlist: {e}")
        
        return videos
    
    def search_track(self, metadata: TrackMetadata) -> Optional[str]:
        """
        Search for a track on YouTube.
        
        Args:
            metadata: Track metadata from Spotify
        
        Returns:
            YouTube video URL of best match, or None
        """
        # Build search query
        query = f"{metadata.artist} - {metadata.title}"
        
        # Configure yt-dlp for search
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search YouTube
                search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)
                
                if not search_results or 'entries' not in search_results:
                    return None
                
                # Filter and rank results
                best_match = self._find_best_match(
                    search_results['entries'],
                    metadata
                )
                
                if best_match:
                    return f"https://www.youtube.com/watch?v={best_match['id']}"
                
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None
        
        return None
    
    def _parse_title(self, title: str) -> tuple[str, str]:
        """
        Parse YouTube title to extract artist and song name.
        Common formats: "Artist - Song", "Artist: Song", "Song by Artist"
        
        Args:
            title: YouTube video title
        
        Returns:
            Tuple of (artist, song_title)
        """
        # Try to split by common delimiters
        for delimiter in [' - ', ' – ', ': ', ' : ']:
            if delimiter in title:
                parts = title.split(delimiter, 1)
                return (parts[0].strip(), parts[1].strip())
        
        # If no delimiter found, use the whole title as song name
        return ("Unknown Artist", title.strip())
    
    def _find_best_match(
        self,
        results: List[Dict],
        metadata: TrackMetadata
    ) -> Optional[Dict]:
        """
        Find the best matching result from search results.
        
        Args:
            results: List of search results from yt-dlp
            metadata: Original track metadata
        
        Returns:
            Best matching result dictionary, or None
        """
        if not results:
            return None
        
        # Filter out live performances, remixes, covers
        exclude_keywords = ['live', 'remix', 'cover', 'instrumental', 'karaoke', 'lyrics']
        
        filtered_results = []
        for result in results:
            title = result.get('title', '').lower()
            
            # Skip if contains excluded keywords
            if any(keyword in title for keyword in exclude_keywords):
                continue
            
            filtered_results.append(result)
        
        # If filtering removed all results, use original list
        if not filtered_results:
            filtered_results = results
        
        # Return first filtered result (yt-dlp returns relevance-sorted results)
        return filtered_results[0] if filtered_results else None
