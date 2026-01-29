# Music Metadata Fetcher & Audio Processing Pipeline

## 1. Project Overview

This project is a **backend-focused personal application** that allows a user to submit a Spotify track or playlist link and receive corresponding audio files processed from publicly available sources.

At a high level, the application:
- Accepts a Spotify track or playlist URL from a user
- Fetches metadata (title, artist, album, duration) using the Spotify Web API
- Searches for a matching audio source on YouTube / YouTube Music
- Processes the audio into a standard format (e.g., MP3)
- Enriches the audio file with metadata and cover art
- Makes the processed file available for download or streaming

This project is intended **for educational and personal use only**, focusing on system design, asynchronous processing, and media pipelines.

---

## 2. Purpose of the Project

The primary goals of this project are:

- To learn how to design and build a **real-world backend system**
- To work with **third-party APIs** (Spotify)
- To understand **asynchronous job processing** using queues
- To gain experience with **media processing pipelines**
- To practice **containerized development with Docker**

From a learning perspective, the project demonstrates how modern backend services handle:
- Long-running tasks
- External service integration
- Scalability concerns
- Separation of concerns between API and workers

---

## 3. Core Features

- Spotify track and playlist URL parsing
- Metadata extraction (title, artist, album, duration, cover art)
- Asynchronous background processing
- Smart matching of tracks to audio sources
- Audio format conversion
- ID3 metadata tagging
- Playlist batch processing
- Temporary file storage and delivery

---

## 4. Tech Stack

### Backend
- **Python 3.11**
- **FastAPI** – REST API framework
- **Uvicorn** – ASGI server
- **Pydantic** – data validation

### Asynchronous Processing
- **Celery** – background task processing
- **Redis** – message broker and task backend

### External Integrations
- **Spotify Web API** – metadata provider
- **spotipy** – Spotify API Python SDK

### Media Processing
- **yt-dlp** – audio search and extraction
- **FFmpeg** – audio conversion
- **mutagen** – ID3 metadata tagging

### Infrastructure & DevOps
- **Docker** – containerization
- **Docker Compose** – multi-container orchestration
- **Environment variables (.env)** – configuration management

### Storage
- Local filesystem (development)
- Object storage (optional for production)

---

## 5. System Architecture

The application is built using a **distributed but minimal architecture**, separating user-facing API logic from long-running background tasks.

### High-Level Architecture

```
Client (Browser / Frontend)
        │
        ▼
FastAPI Backend (API Layer)
        │
        ▼
Redis (Message Broker)
        │
        ▼
Celery Workers (Media Processing)
        │
        ▼
Storage (Audio Files)
```

---

## 6. Architectural Components

### 6.1 API Layer (FastAPI)

Responsibilities:
- Accept user input (Spotify URLs)
- Validate requests
- Fetch metadata from Spotify
- Create background jobs
- Return job status and download links

The API layer is **non-blocking** and does not perform heavy media processing.

---

### 6.2 Task Queue (Redis + Celery)

Responsibilities:
- Handle long-running tasks asynchronously
- Queue individual tracks from playlists
- Enable parallel processing
- Improve system responsiveness

Redis acts as the broker, while Celery manages task execution.

---

### 6.3 Worker Layer (Celery Workers)

Responsibilities:
- Search for matching audio sources
- Download and extract audio
- Convert audio formats
- Embed metadata and cover art
- Save final files to storage

Workers are horizontally scalable and isolated from the API.

---

### 6.4 Media Processing Pipeline

Steps:
1. Receive track metadata
2. Perform YouTube search
3. Select best matching result
4. Download audio stream
5. Convert audio format using FFmpeg
6. Embed ID3 tags and album art
7. Save processed file

---

### 6.5 Storage Layer

Responsibilities:
- Store processed audio files
- Allow API and workers to share access
- Enable file streaming or download

In development, this is implemented using a shared Docker volume.

---

## 7. Docker-Based Setup

The system is containerized to ensure consistency and ease of setup.

### Containers
- **API container** – FastAPI application
- **Worker container** – Celery workers
- **Redis container** – message broker

### Benefits of Docker
- Consistent development environment
- Simplified dependency management
- Easy local setup with one command
- Clear separation of services

---

## 8. Project Structure (Simplified)

```
music-project/
│
├── app/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── tasks/
│   └── core/
│
├── storage/
│   └── downloads/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 9. Notes on Scope and Usage

- This project is designed for **learning and experimentation**
- It is not intended for public deployment or commercial use
- Audio files should be treated as temporary artifacts
- The system avoids permanent storage and indexing

---

## 10. Summary

This project demonstrates how to design and implement a modern backend system involving:
- External APIs
- Asynchronous processing
- Media pipelines
- Containerized infrastructure

It serves as a strong foundation for understanding real-world backend engineering patterns and can be extended with additional features such as authentication, job tracking, and cloud storage integration.

