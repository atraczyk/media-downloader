import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  validateUrl: (url: string) =>
    ipcRenderer.invoke('download:validate-url', url),

  browseFolder: () =>
    ipcRenderer.invoke('download:browse-folder'),

  startDownload: (request: unknown) =>
    ipcRenderer.invoke('download:start', request),

  getStatus: () =>
    ipcRenderer.invoke('download:get-status'),

  onProgress: (cb: (data: unknown) => void) =>
    ipcRenderer.on('download:progress', (_, data) => cb(data)),

  onTranscript: (cb: (data: unknown) => void) =>
    ipcRenderer.on('download:transcript', (_, data) => cb(data)),

  onComplete: (cb: (data: unknown) => void) =>
    ipcRenderer.on('download:complete', (_, data) => cb(data)),

  onLog: (cb: (msg: string) => void) =>
    ipcRenderer.on('download:log', (_, msg) => cb(msg)),

  removeAllListeners: (channel: string) =>
    ipcRenderer.removeAllListeners(channel),
})
