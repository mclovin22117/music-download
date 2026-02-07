# Music Downloader - Simple Standalone Version

## 🚀 Quick Start (No Docker, No Electron - Just Python!)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn requests beautifulsoup4 yt-dlp mutagen
```

### 2. Run the App
```bash
python3 run.py
```

### 3. Use the Web UI
- The app will automatically open in your browser at **http://localhost:8000**
- Paste a Spotify or YouTube URL
- Click "Download Track"
- Music saves to `~/Music/Music Downloader/`

## ✨ Features

- ✅ **No setup needed** - Just run one Python file
- ✅ **Works in any browser** - Chrome, Firefox, Safari, etc.
- ✅ **Spotify support** - Scrapes metadata (no API key needed)
- ✅ **YouTube support** - Direct downloads
- ✅ **Auto metadata** - Artist, title, album art embedded
- ✅ **MP3 format** - Best audio quality

## 📖 How It Works

1. Paste Spotify URL → Scrapes song info from Spotify web page
2. Searches YouTube for the song
3. Downloads audio using yt-dlp
4. Converts to MP3
5. Adds metadata (artist, title, cover art)
6. Saves to your Music folder

## 🎯 Usage

### Download a Single Track
1. Copy track URL from Spotify or YouTube
2. Paste in the input field
3. Click "Download Track"
4. Wait for completion

### Download a Playlist
1. Copy playlist URL from Spotify
2. Paste in the input field
3. Click "Download Playlist"
4. All tracks download automatically

## 🛠️ Troubleshooting

**App won't start:**
```bash
# Make sure Python 3.8+ is installed
python3 --version

# Install dependencies again
pip3 install --upgrade fastapi uvicorn requests beautifulsoup4 yt-dlp mutagen
```

**Downloads fail:**
- Check your internet connection
- Try a different URL
- Make sure yt-dlp is up to date: `pip3 install --upgrade yt-dlp`

**Port 8000 already in use:**
Edit `run.py` and change the port number in the last line.

## 📦 For Developers

### Project Structure
```
music-download/
├── run.py                    # Main entry point - RUN THIS!
├── app/
│   ├── main_standalone.py    # FastAPI backend
│   ├── services/             # Spotify & YouTube services
│   └── utils/                # Download utilities
└── frontend/                 # Web UI files
    ├── index.html
    ├── styles.css
    └── app.js
```

### API Endpoints
- `GET /` - Web UI
- `GET /health` - Health check
- `POST /api/tracks/download` - Download single track
- `GET /api/tracks/status/{task_id}` - Check download status
- `POST /api/playlists/download` - Download playlist

## 🎵 Enjoy Your Music!

No complex setup, no Docker, no Electron - just a simple Python app that works.

Press `CTRL+C` in the terminal to stop the server when you're done.
