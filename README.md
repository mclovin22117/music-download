# Music Downloader

A simple web-based music downloader that fetches tracks from Spotify and YouTube URLs.

## Prerequisites

- **Docker** and **Docker Compose** installed on your system
- Internet connection

## Quick Start

### 1. Start the Project

Open a terminal in the project directory and run:

```bash
docker-compose up -d
```

This will start all services in the background:
- Redis (database)
- FastAPI API server (port 8000)
- 2 Celery workers (for background downloads)

### 2. Access the Web UI

Open your browser and go to:

```
http://localhost:8000
```

### 3. Download Music

1. Paste a Spotify or YouTube URL in the input field
2. Click the "Download" button
3. Wait for the download to complete
4. Downloaded files are saved in the `downloads/` folder

**Supported URLs:**
- Spotify tracks: `https://open.spotify.com/track/...`
- YouTube videos: `https://www.youtube.com/watch?v=...`

## Managing the Project

### Stop the Project

```bash
docker-compose down
```

### python env
source venv/bin/activate
### to deactivate venv
deactivate

### Restart After Changes

If you make code changes:

```bash
docker-compose restart api worker
```

### View Logs

To see what's happening:

```bash
# View all logs
docker-compose logs -f

# View only API logs
docker-compose logs -f api

# View only worker logs
docker-compose logs -f worker
```

### Check Container Status

```bash
docker-compose ps
```

All containers should show "Up" status.

## Troubleshooting

### Port 8000 Already in Use

If you get an error that port 8000 is already in use:

```bash
# Stop the containers
docker-compose down

# Check what's using port 8000
sudo lsof -i :8000

# Kill the process or change the port in docker-compose.yml
```

### Downloads Failing

1. Check the worker logs: `docker-compose logs worker`
2. Make sure you have internet connection
3. Verify the URL is correct and accessible

### Containers Won't Start

```bash
# Clean up and restart
docker-compose down
docker-compose up -d

# If still failing, rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Project Structure

```
music-download/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/endpoints/       # API routes
│   ├── services/            # Spotify & YouTube services
│   ├── workers/             # Celery tasks
│   └── utils/               # Helper functions
├── downloads/               # Downloaded music files
├── docker-compose.yml       # Docker configuration
├── index.html               # Web UI
└── README.md               # This file
```

## Features

- ✅ Download from Spotify (web scraping, no API key needed)
- ✅ Download from YouTube (yt-dlp)
- ✅ Automatic metadata tagging (artist, title, album)
- ✅ Web-based UI
- ✅ Background task processing
- ✅ MP3 format output

## Tech Stack

- **Backend**: FastAPI + Python
- **Task Queue**: Celery + Redis
- **Downloads**: yt-dlp
- **Scraping**: BeautifulSoup4
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker Compose

## Legal Notice

**For personal use only.** Respect copyright laws and artists' rights. This tool is intended for:
- Personal backups of purchased music
- Downloading Creative Commons content
- Educational purposes

Do NOT use for piracy or commercial distribution.

---

**Need help?** Check the logs with `docker-compose logs -f` to see what's happening.
