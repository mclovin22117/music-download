"""
YouTube search service for finding matching audio.
"""
import yt_dlp
from typing import Optional, List, Dict
from app.models import TrackMetadata


class YouTubeService:
    """Service for searching YouTube for matching tracks."""
    
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
