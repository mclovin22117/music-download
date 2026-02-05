const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    getBackendUrl: () => ipcRenderer.invoke('get-backend-url')
});
