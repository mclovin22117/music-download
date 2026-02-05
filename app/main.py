"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # Restrict to local frontend
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Include routers
app.include_router(tracks.router, prefix="/api/v1/tracks", tags=["tracks"])
app.include_router(playlists.router, prefix="/api/v1/playlists", tags=["playlists"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Music Download API",
        "version": settings.api_version,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
