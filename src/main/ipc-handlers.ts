import { ipcMain, dialog, BrowserWindow, shell, app } from 'electron'
import path from 'path'
import { getMediaInfo, downloadMedia, cancelDownload } from '../core/downloader.js'
import { fetchTranscript } from '../core/transcript.js'
import { saveTranscript, ensureDirectory } from '../core/file-manager.js'
import { DownloadRequest } from '../core/types.js'

let isDownloading = false

function safeSend(win: BrowserWindow, channel: string, data: unknown): void {
  if (!win.isDestroyed()) win.webContents.send(channel, data)
}

export function setupIpcHandlers(): void {
  ipcMain.handle('download:validate-url', async (_, url: string) => {
    const [info, error] = await getMediaInfo(url)
    if (error || !info) return { valid: false, error: error ?? 'Unknown error' }
    return { valid: true, title: info.title, duration: info.duration, uploader: info.uploader, isAudioOnly: info.isAudioOnly }
  })

  ipcMain.handle('download:browse-folder', async (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    if (!win) return { success: false }
    const result = await dialog.showOpenDialog(win, { properties: ['openDirectory'] })
    if (result.canceled || !result.filePaths[0]) return { success: false }
    return { success: true, path: result.filePaths[0] }
  })

  ipcMain.handle('download:start', async (event, request: DownloadRequest) => {
    if (isDownloading) return { success: false, error: 'Download already in progress' }

    const win = BrowserWindow.fromWebContents(event.sender)
    if (!win) return { success: false, error: 'Window unavailable' }

    const resolvedRequest = { ...request, destination: path.resolve(request.destination) }

    const [dirOk, dirErr] = await ensureDirectory(resolvedRequest.destination)
    if (!dirOk) return { success: false, error: `Cannot create directory: ${dirErr}` }

    isDownloading = true

    // Run async in background — reply immediately so renderer can show progress
    ;(async () => {
      try {
        let transcriptResult = null

        if (resolvedRequest.transcriptEnabled) {
          safeSend(win, 'download:progress', {
            status: 'processing', progress: 0.05, message: 'Fetching transcript...',
          })
          transcriptResult = await fetchTranscript(resolvedRequest.url)
          safeSend(win, 'download:transcript', transcriptResult)
        }

        const [success, result] = await downloadMedia(
          resolvedRequest,
          (p) => safeSend(win, 'download:progress', p),
          (msg) => safeSend(win, 'download:log', msg)
        )

        if (success && transcriptResult?.text) {
          await saveTranscript(transcriptResult.text, result, request.destination)
        }

        safeSend(win, 'download:complete', {
          success,
          message: success ? 'Download complete!' : result,
          filename: success ? result : undefined,
        })
      } finally {
        isDownloading = false
      }
    })()

    return { success: true }
  })

  ipcMain.handle('download:get-status', () => ({ isDownloading }))

  ipcMain.handle('app:default-dest', () =>
    path.join(app.getPath('downloads'), 'media-downloader')
  )

  ipcMain.handle('download:cancel', () => {
    cancelDownload()
  })

  ipcMain.handle('shell:show-item', (_, filePath: string) => {
    shell.showItemInFolder(filePath)
  })

  ipcMain.handle('window:minimize', (event) => {
    BrowserWindow.fromWebContents(event.sender)?.minimize()
  })
  ipcMain.handle('window:maximize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    if (!win) return
    win.isMaximized() ? win.unmaximize() : win.maximize()
  })
  ipcMain.handle('window:close', (event) => {
    BrowserWindow.fromWebContents(event.sender)?.close()
  })
  ipcMain.handle('window:is-maximized', (event) => {
    return BrowserWindow.fromWebContents(event.sender)?.isMaximized() ?? false
  })
}
