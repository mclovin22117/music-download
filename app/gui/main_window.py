"""
Desktop GUI for Music Downloader using PyQt6.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit, 
    QLabel, QProgressBar, QListWidget
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from app.services.spotify_service import SpotifyService
from app.services.youtube_service import YouTubeService
from app.utils.downloader import AudioDownloader
from app.models import TrackMetadata


class DownloadWorker(QThread):
    """Background thread for downloading music."""
    
    progress = pyqtSignal(str)  # Status updates
    finished = pyqtSignal(dict)  # Download result
    error = pyqtSignal(str)  # Error message
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        # Initialize downloader with Music directory
        download_dir = Path.home() / "Music" / "Music Downloader"
        self.downloader = AudioDownloader(download_dir)

    def run(self):
        """Execute download in background."""
        try:
            self.progress.emit("🔍 Analyzing URL...")
            
            if "spotify.com" in self.url:
                # Spotify download
                self.progress.emit("🎵 Fetching Spotify metadata...")
                spotify = SpotifyService()
                metadata_dict = spotify.get_track_metadata(self.url)
                
                # Map Spotify field names to TrackMetadata field names
                mapped_metadata = {
                    'title': metadata_dict.get('name', 'Unknown'),
                    'artist': metadata_dict.get('artist', 'Unknown Artist'),
                    'album': metadata_dict.get('album', 'Unknown Album'),
                    'year': metadata_dict.get('year'),
                    'duration_ms': metadata_dict.get('duration') or 0,
                    'spotify_id': metadata_dict.get('track_id', ''),
                    'cover_art_url': metadata_dict.get('cover_url')
                }
                
                metadata = TrackMetadata(**mapped_metadata)
                
                self.progress.emit(f"🔎 Searching YouTube for: {metadata.artist} - {metadata.title}")
                youtube = YouTubeService()
                youtube_url = youtube.search_track(metadata)
                
                if not youtube_url:
                    self.error.emit("Could not find track on YouTube")
                    return
                
                self.progress.emit("⬇️ Downloading audio...")
                file_path = self.downloader.download(youtube_url, metadata)
                
                if file_path:
                    result = {
                        "track": metadata.title,
                        "artist": metadata.artist,
                        "file_path": str(file_path)
                    }
                    self.finished.emit(result)
                else:
                    self.error.emit("Download failed - no file created")
                
            else:
                # Direct YouTube download
                self.progress.emit("⬇️ Downloading from YouTube...")
                
                try:
                    # Get video info first
                    youtube = YouTubeService()
                    video_metadata = youtube.get_video_metadata(self.url)
                    
                    if video_metadata:
                        # Use extracted metadata
                        metadata = video_metadata
                        self.progress.emit(f"Found: {metadata.artist} - {metadata.title}")
                    else:
                        # Fallback: Create basic metadata
                        metadata = TrackMetadata(
                            title="Unknown",
                            artist="Unknown",
                            album="Unknown",
                            year=None,
                            duration_ms=0,
                            spotify_id='',
                            cover_art_url=None
                        )
                except Exception as e:
                    print(f"Could not get YouTube metadata: {e}")
                    # Fallback metadata
                    metadata = TrackMetadata(
                        title="Unknown",
                        artist="Unknown",
                        album="Unknown",
                        year=None,
                        duration_ms=0,
                        spotify_id='',
                        cover_art_url=None
                    )
                
                file_path = self.downloader.download(self.url, metadata)
                
                if file_path:
                    result = {
                        "track": metadata.title,
                        "artist": metadata.artist,
                        "file_path": str(file_path)
                    }
                    self.finished.emit(result)
                else:
                    self.error.emit("Download failed - no file created")
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.download_worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🎵 Music Downloader")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Music Downloader")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #1DB954; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Download music from Spotify and YouTube")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # URL input section
        input_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Spotify or YouTube URL here...")
        self.url_input.setMinimumHeight(40)
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #1DB954;
            }
        """)
        input_layout.addWidget(self.url_input)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setMinimumHeight(40)
        self.download_btn.setMinimumWidth(120)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #1aa34a;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)
        input_layout.addWidget(self.download_btn)
        
        layout.addLayout(input_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #1DB954;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.status_text)
        
        # Download history
        history_label = QLabel("Download History:")
        history_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e8f5e9;
                color: black;
            }
        """)
        layout.addWidget(self.history_list)
        
        # Download folder info
        download_path = Path.home() / "Music" / "Music Downloader"
        download_path.mkdir(parents=True, exist_ok=True)
        
        footer = QLabel(f"Downloads saved to: {download_path}")
        footer.setStyleSheet("color: #666; font-size: 11px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
    
    def start_download(self):
        """Start downloading the track."""
        url = self.url_input.text().strip()
        
        if not url:
            self.update_status("❌ Please enter a URL")
            return
        
        if not ("spotify.com" in url or "youtube.com" in url or "youtu.be" in url):
            self.update_status("❌ Invalid URL. Please use Spotify or YouTube links.")
            return
        
        # Disable UI during download
        self.download_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start download in background thread
        self.download_worker = DownloadWorker(url)
        self.download_worker.progress.connect(self.update_status)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        self.download_worker.start()
    
    def update_status(self, message: str):
        """Update status text."""
        self.status_text.append(message)
        # Auto-scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
    
    def download_finished(self, result: dict):
        """Handle successful download."""
        track = result.get("track", "Unknown")
        artist = result.get("artist", "Unknown")
        
        self.update_status(f"✅ Downloaded: {artist} - {track}")
        
        # Add to history
        self.history_list.insertItem(0, f"✓ {artist} - {track}")
        
        # Re-enable UI
        self.reset_ui()
    
    def download_error(self, error: str):
        """Handle download error."""
        self.update_status(f"❌ Error: {error}")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI after download."""
        self.download_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        self.url_input.clear()
        self.progress_bar.setVisible(False)


def main():
    """Run the desktop application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()