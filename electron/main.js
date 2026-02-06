const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let mainWindow;
let backendProcess;
const isDev = !app.isPackaged;

function getBackendPath() {
    if (isDev) {
        // In development, use Docker
        return null;
    }
    
    // In production, use bundled executable
    const resourcePath = process.resourcesPath;
    const backendPath = path.join(resourcePath, 'backend', 'music-downloader');
    
    if (process.platform === 'win32') {
        return backendPath + '.exe';
    }
    return backendPath;
}

function startBackend() {
    if (isDev) {
        console.log('Development mode: Backend should be running via docker-compose');
        return;
    }

    const backendPath = getBackendPath();
    
    if (!fs.existsSync(backendPath)) {
        console.error('Backend executable not found:', backendPath);
        console.error('Expected at:', backendPath);
        console.error('Resource path:', process.resourcesPath);
        return;
    }

    console.log('Starting backend:', backendPath);
    
    backendProcess = spawn(backendPath, [], {
        env: {
            ...process.env
        },
        cwd: path.dirname(backendPath)
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`Backend error: ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend exited with code ${code}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'icon.png'),
        title: 'Music Downloader',
        backgroundColor: '#667eea'
    });

    // In production, frontend is in resources/app/frontend
    // In dev, it's in ../frontend
    const frontendPath = isDev 
        ? path.join(__dirname, '..', 'frontend', 'index.html')
        : path.join(process.resourcesPath, 'frontend', 'index.html');

    console.log('Loading frontend from:', frontendPath);
    console.log('Frontend exists:', fs.existsSync(frontendPath));

    mainWindow.loadFile(frontendPath).catch(err => {
        console.error('Failed to load frontend:', err);
    });

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    startBackend();
    
    // Wait 2 seconds for backend to start
    setTimeout(createWindow, 2000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
    
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
});

// Handle IPC messages from renderer
ipcMain.handle('get-backend-url', () => {
    return 'http://localhost:8000';
});