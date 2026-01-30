"""
Service for embedding metadata into audio files.
"""
import requests
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from typing import Optional

from app.models import TrackMetadata


class MetadataService:
    """Service for embedding metadata into MP3 files."""
    
    @staticmethod
    def embed_metadata(file_path: Path, metadata: TrackMetadata) -> None:
        """
        Embed metadata and cover art into an MP3 file.
        
        Args:
            file_path: Path to the MP3 file
            metadata: Track metadata to embed
        """
        try:
            # Load the MP3 file
            audio = MP3(file_path, ID3=ID3)
            
            # Add ID3 tags if not present
            if audio.tags is None:
                audio.add_tags()
            
            # Set basic metadata
            audio.tags.add(TIT2(encoding=3, text=metadata.title))
            audio.tags.add(TPE1(encoding=3, text=metadata.artist))
            audio.tags.add(TALB(encoding=3, text=metadata.album))
            
            # Download and embed cover art
            if metadata.cover_art_url:
                cover_data = MetadataService._download_cover_art(metadata.cover_art_url)
                if cover_data:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=cover_data
                        )
                    )
            
            # Save the tags
            audio.save()
            
        except Exception as e:
            print(f"Error embedding metadata: {e}")
            raise
    
    @staticmethod
    def _download_cover_art(url: str) -> Optional[bytes]:
        """
        Download cover art from URL.
        
        Args:
            url: URL of the cover art image
        
        Returns:
            Image data as bytes, or None if download fails
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading cover art: {e}")
            return None
