# Music Download API

A FastAPI-based backend application that downloads music from Spotify URLs using YouTube as the audio source.

## Features

- Download single tracks from Spotify URLs
- Download entire playlists
- Automatic YouTube search and matching
- MP3 conversion with metadata embedding
- Album art embedding
- Async task processing with Celery
- Docker-based deployment

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

### Getting Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy the Client ID and Client Secret

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your Spotify credentials
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
```
POST /api/v1/tracks/download
Content-Type: application/json

{
  "spotify_url": "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
}
```

### Download Playlist
```
POST /api/v1/playlists/download
Content-Type: application/json

{
  "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
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
