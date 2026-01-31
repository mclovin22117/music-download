# Music Download API

A FastAPI-based backend application that downloads music from Spotify or YouTube URLs and converts them to MP3 with metadata.

## Features

- ✅ Download from **Spotify track URLs** (with automatic YouTube matching)
- ✅ Download from **Spotify playlists**
- ✅ Download from **YouTube video URLs** (direct)
- ✅ Download from **YouTube playlists** (direct)
- ✅ MP3 conversion with metadata embedding
- ✅ Album art embedding
- ✅ Async task processing with Celery
- ✅ Docker-based deployment

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

## License

Educational project - Not for commercial use.
