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
    
    console.log('=== Backend Startup Debug ===');
    console.log('Platform:', process.platform);
    console.log('Packaged:', app.isPackaged);
    console.log('Resource path:', process.resourcesPath);
    console.log('Backend path:', backendPath);
    console.log('Backend exists:', fs.existsSync(backendPath));
    
    if (!fs.existsSync(backendPath)) {
        console.error('❌ Backend executable not found!');
        console.error('Expected at:', backendPath);
        
        // Try to list what's actually in the backend directory
        const backendDir = path.dirname(backendPath);
        if (fs.existsSync(backendDir)) {
            console.log('Files in backend dir:', fs.readdirSync(backendDir));
        } else {
            console.error('Backend directory does not exist:', backendDir);
        }
        return;
    }

    console.log('✅ Backend executable found, starting...');
    
    backendProcess = spawn(backendPath, [], {
        env: {
            ...process.env
        },
        cwd: path.dirname(backendPath)
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`[Backend]: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`[Backend Error]: ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`[Backend]: Process exited with code ${code}`);
    });

    backendProcess.on('error', (err) => {
        console.error(`[Backend]: Failed to start:`, err);
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
    console.log('=== App Ready ===');
    console.log('Is packaged:', app.isPackaged);
    console.log('Is dev mode:', isDev);
    
    startBackend();
    
    // Wait longer for backend to start (5 seconds)
    console.log('Waiting 5 seconds for backend to initialize...');
    setTimeout(() => {
        console.log('Creating window...');
        createWindow();
    }, 5000);

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