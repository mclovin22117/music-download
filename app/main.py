"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.api.endpoints import tracks, playlists

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Backend API for downloading music from Spotify URLs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Include routers
app.include_router(tracks.router, prefix="/api/v1/tracks", tags=["tracks"])
app.include_router(playlists.router, prefix="/api/v1/playlists", tags=["playlists"])


@app.get("/")
async def serve_frontend():
    """Serve the web UI."""
    return FileResponse('index.html')


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}