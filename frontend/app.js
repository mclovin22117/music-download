const API_BASE = 'http://localhost:8000';
const downloadHistory = [];

// DOM Elements
const urlInput = document.getElementById('urlInput');
const downloadBtn = document.getElementById('downloadBtn');
const playlistBtn = document.getElementById('playlistBtn');
const statusSection = document.getElementById('status');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');
const progressFill = document.getElementById('progressFill');
const trackInfo = document.getElementById('trackInfo');
const historyList = document.getElementById('historyList');

// Event Listeners
downloadBtn.addEventListener('click', () => handleDownload(false));
playlistBtn.addEventListener('click', () => handleDownload(true));
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleDownload(false);
});

async function handleDownload(isPlaylist) {
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }

    // Validate URL
    if (!isValidUrl(url)) {
        showError('Invalid URL. Please enter a Spotify or YouTube URL');
        return;
    }

    // Disable inputs
    setLoading(true);
    showStatus('Initializing download...', '⏳', 10);

    try {
        const endpoint = isPlaylist ? '/api/playlists/download' : '/api/tracks/download';
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (isPlaylist) {
            handlePlaylistDownload(data);
        } else {
            checkTaskStatus(data.task_id);
        }
        
    } catch (error) {
        showError(`Failed to start download: ${error.message}`);
        setLoading(false);
    }
}

async function checkTaskStatus(taskId) {
    const maxAttempts = 300; // 5 minutes max
    let attempts = 0;

    const interval = setInterval(async () => {
        attempts++;
        
        if (attempts > maxAttempts) {
            clearInterval(interval);
            showError('Download timeout. Please try again.');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/api/tracks/status/${taskId}`);
            const data = await response.json();

            updateProgress(data);

            if (data.status === 'completed') {
                clearInterval(interval);
                showSuccess(data);
                addToHistory(data, 'success');
                setLoading(false);
                urlInput.value = '';
            } else if (data.status === 'failed') {
                clearInterval(interval);
                showError(`Download failed: ${data.error || 'Unknown error'}`);
                addToHistory(data, 'error');
                setLoading(false);
            }
        } catch (error) {
            console.error('Status check error:', error);
        }
    }, 1000);
}

function handlePlaylistDownload(data) {
    showStatus(`Downloading playlist: ${data.total_tracks} tracks`, '📋', 50);
    
    // Track all subtasks
    const tasks = data.tasks;
    let completed = 0;
    let failed = 0;

    tasks.forEach(task => {
        setTimeout(() => checkSubTaskStatus(task.task_id, tasks.length, () => {
            completed++;
            const progress = (completed / tasks.length) * 100;
            showStatus(`Downloaded ${completed}/${tasks.length} tracks`, '⬇️', progress);
            
            if (completed + failed === tasks.length) {
                showSuccess({ 
                    track: `Playlist download complete: ${completed} succeeded, ${failed} failed` 
                });
                setLoading(false);
                urlInput.value = '';
            }
        }, () => {
            failed++;
        }), 100);
    });
}

async function checkSubTaskStatus(taskId, totalTracks, onSuccess, onFail) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/tracks/status/${taskId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                onSuccess();
            } else if (data.status === 'failed') {
                clearInterval(interval);
                onFail();
            }
        } catch (error) {
            console.error('Subtask check error:', error);
        }
    }, 2000);
}

function updateProgress(data) {
    const statusMap = {
        'pending': { icon: '⏳', text: 'Pending...', progress: 10 },
        'started': { icon: '🔍', text: 'Fetching metadata...', progress: 30 },
        'PROGRESS': { 
            icon: '⬇️', 
            text: data.meta?.step || 'Downloading...', 
            progress: 60 
        }
    };

    const status = statusMap[data.status] || { icon: '⏳', text: data.status, progress: 50 };
    
    let infoText = '';
    if (data.track) {
        infoText = `Track: ${data.track}`;
        if (data.artist) infoText += ` - ${data.artist}`;
    }

    showStatus(status.text, status.icon, status.progress, infoText);
}

function showStatus(text, icon, progress, info = '') {
    statusSection.classList.remove('hidden');
    statusText.textContent = text;
    statusIcon.textContent = icon;
    progressFill.style.width = `${progress}%`;
    trackInfo.textContent = info;
}

function showSuccess(data) {
    showStatus('Download completed!', '✅', 100, data.track || '');
    setTimeout(() => {
        statusSection.classList.add('hidden');
    }, 5000);
}

function showError(message) {
    showStatus(message, '❌', 0);
    setTimeout(() => {
        statusSection.classList.add('hidden');
    }, 5000);
}

function setLoading(loading) {
    downloadBtn.disabled = loading;
    playlistBtn.disabled = loading;
    urlInput.disabled = loading;
}

function isValidUrl(url) {
    return url.includes('spotify.com') || 
           url.includes('youtube.com') || 
           url.includes('youtu.be');
}

function addToHistory(data, status) {
    downloadHistory.unshift({
        track: data.track || 'Unknown',
        artist: data.artist || '',
        status: status,
        time: new Date().toLocaleTimeString()
    });

    renderHistory();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderHistory() {
    if (downloadHistory.length === 0) {
        historyList.innerHTML = '<p class="empty-state">No downloads yet</p>';
        return;
    }

    historyList.innerHTML = downloadHistory.map(item => `
        <div class="history-item">
            <div class="history-item-info">
                <div class="history-item-title">${escapeHtml(item.track)}</div>
                ${item.artist ? `<div class="history-item-artist">${escapeHtml(item.artist)}</div>` : ''}
            </div>
            <div class="history-item-status status-${item.status}">
                ${item.status === 'success' ? '✓ Downloaded' : '✗ Failed'}
            </div>
        </div>
    `).join('');
}

// Check if backend is running on load
window.addEventListener('load', async () => {
    try {
        await fetch(`${API_BASE}/health`);
        console.log('✓ Backend connected');
    } catch (error) {
        showError('⚠️ Backend not running. Please start the service first.');
    }
});
