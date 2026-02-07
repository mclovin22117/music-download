#!/bin/bash
# Simple startup script

echo "======================================"
echo "🎵 Music Downloader"
echo "======================================"
echo ""
echo "Starting service..."
echo ""

cd "$(dirname "$0")"

# Start with docker-compose (backend already configured)
docker-compose up -d

sleep 3

echo "✅ Service started!"
echo ""
echo "🌐 Open in your browser:"
echo "   http://localhost:8000"
echo ""
echo "📁 Downloads save to: ~/Music/Music Downloader/"
echo ""
echo "To stop: docker-compose down"
echo ""
