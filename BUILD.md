# Building Music Downloader

## Prerequisites

- **Node.js** 18+ (for Electron)
- **Python** 3.11+ (for backend)
- **Docker** (optional, for development)

---

## Development Mode

### 1. Start Backend (Docker)
```bash
docker-compose up -d
```

### 2. Run Electron App
```bash
cd electron
npm install
npm start
```

The app will open and connect to `http://localhost:8000`

---

## Production Build

### Build Backend Executable

**Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt pyinstaller

pyinstaller --onefile \
  --name music-downloader \
  --add-data "app:app" \
  --hidden-import=celery \
  --hidden-import=uvicorn \
  --hidden-import=fastapi \
  app/main.py

# Output: dist/music-downloader
```

**Windows (on Windows machine):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt pyinstaller

pyinstaller --onefile ^
  --name music-downloader ^
  --add-data "app;app" ^
  --hidden-import=celery ^
  --hidden-import=uvicorn ^
  --hidden-import=fastapi ^
  app/main.py

# Output: dist\music-downloader.exe
```

### Build Electron App

**Copy backend executable:**
```bash
mkdir -p electron/backend
cp dist/music-downloader electron/backend/
```

**Build for your platform:**
```bash
cd electron
npm install

# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

**Outputs:**
- Windows: `electron/dist/Music Downloader Setup.exe`
- macOS: `electron/dist/Music Downloader.dmg`
- Linux: `electron/dist/Music Downloader.AppImage`

---

## Automated Release (GitHub Actions)

### Setup

1. Push code to GitHub
2. Create a release tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. GitHub Actions will automatically:
   - Build backend for all platforms
   - Build Electron apps (Windows, macOS, Linux)
   - Create GitHub release with installers

### Manual Trigger

Go to: **Actions → Build and Release → Run workflow**

---

## Testing Builds

### Windows
```
Music Downloader Setup.exe
```
Double-click to install, then launch from Start Menu

### macOS
```
Music Downloader.dmg
```
Mount DMG, drag to Applications

### Linux
```bash
chmod +x Music\ Downloader.AppImage
./Music\ Downloader.AppImage
```

---

## Troubleshooting

**Backend not starting:**
- Check if Redis is installed (production builds need Redis)
- Check backend logs in app data folder

**Electron build fails:**
- Clear `node_modules`: `rm -rf node_modules && npm install`
- Update electron-builder: `npm install -D electron-builder@latest`

**PyInstaller missing modules:**
- Add `--hidden-import=module_name` to build command
- Check `import` statements in your code
