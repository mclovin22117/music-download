#!/usr/bin/env python3
"""
Simple music downloader - just run this file!
No Docker, no complex setup - just Python.
"""
import sys
import os
import webbrowser
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main_standalone import app
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🎵 Music Downloader Starting...")
    print("=" * 60)
    
    # Create downloads folder
    download_dir = Path.home() / "Music" / "Music Downloader"
    download_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Downloads will be saved to: {download_dir}")
    
    # Get local IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\n🌐 Starting web server...")
    print(f"   Local: http://localhost:8000")
    print(f"   Network: http://{local_ip}:8000")
    print(f"\n✨ Opening web browser...")
    print(f"💡 Press CTRL+C to stop the server\n")
    print("=" * 60)
    
    # Open browser after a short delay
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:8000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
