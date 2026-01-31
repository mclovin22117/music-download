# 🎵 Music Download API

A FastAPI-based backend application that downloads music from Spotify or YouTube URLs and converts them to MP3 with metadata.

> **⚠️ Educational Purpose Only**: This project is for learning backend architecture, async processing, and API design. Please respect copyright laws and use responsibly.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- ✅ Download from **Spotify track URLs** (with automatic YouTube matching)
- ✅ Download from **Spotify playlists**
- ✅ Download from **YouTube video URLs** (direct)
- ✅ Download from **YouTube playlists** (direct)
- ✅ MP3 conversion with metadata embedding
- ✅ Album art embedding
- ✅ Async task processing with Celery
- ✅ Docker-based deployment
- ✅ REST API with automatic documentation

## Architecture

- **API Layer**: FastAPI for REST endpoints
- **Worker Layer**: Celery for async task processing
- **Message Broker**: Redis for task queue
- **Media Processing**: yt-dlp + FFmpeg for audio extraction
- **Metadata**: Spotify Web API for track info, mutagen for MP3 tagging

## Setup

### Prerequisites

- Docker & Docker Compose
- Spotify Developer Account

### Getting Spotify API Credentials (Optional)

**Note**: Spotify API credentials are only required if you want to download from Spotify URLs. You can use YouTube URLs without any API credentials!

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy the Client ID and Client Secret

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. (Optional) Edit `.env` and add your Spotify credentials if you want Spotify support
4. Build and start the services:
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Download Single Track

**From Spotify:**
```bash
POST /api/v1/tracks/download
Content-Type: application/json

{
  "url": "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
}
```

**From YouTube:**
```bash
POST /api/v1/tracks/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

### Download Playlist

**From Spotify:**
```bash
POST /api/v1/playlists/download
Content-Type: application/json

{
  "url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
}
```

**From YouTube:**
```bash
POST /api/v1/playlists/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/playlist?list=PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG"
}
```

### Check Task Status
```
GET /api/v1/tracks/status/{task_id}
```

## Development

### Running Tests
```bash
pytest tests/
```

### Project Structure
```
music-download/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── services/          # Business logic
│   ├── workers/           # Celery tasks
│   └── utils/             # Utilities
├── docker/                # Dockerfiles
├── downloads/             # Output directory
└── tests/                 # Test files
```

## 📋 Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Task Queue**: Celery + Redis
- **Media Processing**: yt-dlp, FFmpeg, mutagen
- **APIs**: Spotify Web API (optional), YouTube (via yt-dlp)
- **Containerization**: Docker + Docker Compose

## 📸 Screenshots

API automatically generates interactive documentation at `/docs`:
- Swagger UI for testing endpoints
- Real-time task status monitoring
- Request/response examples

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## ⚖️ Legal Disclaimer

This tool is for educational purposes only. Users are responsible for:
- Complying with YouTube's Terms of Service
- Respecting copyright laws in their jurisdiction
- Not using downloaded content for commercial purposes
- Obtaining proper permissions before downloading copyrighted material

The developers assume no liability for misuse of this software.

## 🐛 Known Issues

- Large playlists may take time to process
- Some YouTube videos may be age-restricted or region-locked
- Spotify API has rate limits (handled gracefully)

## 📝 TODO / Future Enhancements

- [ ] Web UI frontend
- [ ] Progress tracking for individual downloads
- [ ] File management API (list, delete downloaded files)
- [ ] Authentication & user accounts
- [ ] Download queue management
- [ ] Playlist synchronization
- [ ] Support for more streaming services

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Be respectful and constructive

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube functionality
- [Spotipy](https://spotipy.readthedocs.io/) for Spotify API wrapper
- [Celery](https://docs.celeryproject.org/) for task queue

---

**Made with ❤️ for learning purposes**
