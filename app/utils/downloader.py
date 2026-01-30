"""
Audio downloader using yt-dlp.
"""
import yt_dlp
from pathlib import Path
from typing import Optional
import re

from app.models import TrackMetadata


class AudioDownloader:
    """Wrapper for yt-dlp to download and convert audio."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize downloader.
        
        Args:
            output_dir: Directory to save downloaded files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, youtube_url: str, metadata: TrackMetadata) -> Optional[Path]:
        """
        Download audio from YouTube and convert to MP3.
        
        Args:
            youtube_url: YouTube video URL
            metadata: Track metadata for naming
        
        Returns:
            Path to downloaded MP3 file, or None if failed
        """
        try:
            # Sanitize filename
            safe_filename = self._sanitize_filename(
                f"{metadata.artist} - {metadata.title}"
            )
            output_template = str(self.output_dir / f"{safe_filename}.%(ext)s")
            
            # Configure yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Return path to the MP3 file
            output_file = self.output_dir / f"{safe_filename}.mp3"
            
            if output_file.exists():
                return output_file
            else:
                return None
                
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Replace multiple spaces with single space
        filename = re.sub(r'\s+', ' ', filename)
        
        # Trim and limit length
        filename = filename.strip()[:200]
        
        return filename
