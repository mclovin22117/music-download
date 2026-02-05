#!/bin/bash

# Build the standalone executable inside Docker
docker build -f Dockerfile.standalone -t music-download-builder .

# Extract the built executable
docker create --name temp-builder music-download-builder
docker cp temp-builder:/build/dist/music-downloader ./music-downloader
docker rm temp-builder

echo "✅ Standalone executable created: ./music-downloader"
echo "Run with: ./music-downloader"
