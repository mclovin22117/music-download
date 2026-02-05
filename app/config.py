"""
Application configuration and environment variables.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    
    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Application
    download_dir: Path = Path("/app/downloads")
    max_workers: int = 4
    
    # API
    api_title: str = "Music Download API"
    api_version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
