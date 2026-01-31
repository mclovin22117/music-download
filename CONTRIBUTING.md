# Contributing to Music Download API

Thank you for considering contributing to this project! 🎵

## Educational Purpose

**Important**: This project is for educational purposes only. It demonstrates backend architecture, async task processing, and API design. Please respect copyright laws and use responsibly.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, Docker version)

### Suggesting Features

1. Open an issue describing:
   - The feature and its benefits
   - Use cases
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/mclovin22117/music-download.git
cd music-download

# Copy environment template
cp .env.example .env

# Start with Docker
docker-compose up --build
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions focused and small

## Testing

- Test your changes with real URLs
- Verify both Spotify and YouTube URLs work
- Check error handling

## Questions?

Feel free to open an issue for any questions!
