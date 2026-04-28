import { spawn } from 'child_process'
import { existsSync } from 'fs'
import path from 'path'
import { DownloadRequest, DownloadProgress, DownloadStatus, DownloadType, MediaInfo } from './types.js'
import { sanitizeFilename } from './file-manager.js'

type ProgressCallback = (progress: DownloadProgress) => void
type LogCallback = (message: string) => void

const BINARY_NAME = process.platform === 'win32' ? 'yt-dlp.exe'
                  : process.platform === 'darwin' ? 'yt-dlp_macos'
                  : 'yt-dlp'

function resolveYtDlp(): string {
  // In packaged Electron, process.resourcesPath is the extraResources destination.
  // In dev/CLI, fall back to the local resources/ folder next to the project root.
  const candidates = [
    process.resourcesPath && path.join(process.resourcesPath, BINARY_NAME),
    path.resolve('resources', BINARY_NAME),
  ].filter(Boolean) as string[]

  return candidates.find(existsSync) ?? BINARY_NAME  // last resort: PATH
}

const YT_DLP = resolveYtDlp()

export async function getMediaInfo(url: string): Promise<[MediaInfo | null, string | null]> {
  return new Promise((resolve) => {
    const chunks: string[] = []
    const errChunks: string[] = []
    const proc = spawn(YT_DLP, ['--dump-json', '--no-playlist', '--no-warnings', '--extractor-args', 'youtube:player_client=android', url])

    proc.stdout.on('data', (d: Buffer) => chunks.push(d.toString()))
    proc.stderr.on('data', (d: Buffer) => errChunks.push(d.toString()))

    proc.on('error', (err) => resolve([null, err.message]))
    proc.on('close', (code) => {
      if (code !== 0) {
        const raw = errChunks.join('').trim() || 'Failed to fetch video info'
        resolve([null, cleanError(raw)])
        return
      }
      try {
        const info = JSON.parse(chunks.join(''))
        resolve([
          {
            title: info.title || 'Unknown',
            duration: info.duration ? Math.floor(info.duration) : undefined,
            uploader: info.uploader || info.channel || undefined,
            sanitizedFilename: sanitizeFilename(info.title || 'download'),
            isAudioOnly: !info.vcodec || info.vcodec === 'none',
          },
          null,
        ])
      } catch {
        resolve([null, 'Failed to parse video info'])
      }
    })
  })
}

let activeProc: ReturnType<typeof spawn> | null = null
let wasCancelled = false

export function cancelDownload(): void {
  if (activeProc) {
    wasCancelled = true
    activeProc.kill()
    activeProc = null
  }
}

export async function downloadMedia(
  request: DownloadRequest,
  onProgress: ProgressCallback,
  onLog: LogCallback
): Promise<[boolean, string]> {
  const [info, infoErr] = await getMediaInfo(request.url)
  if (!info) return [false, infoErr || 'Failed to get video info']

  const { sanitizedFilename: filename } = info
  const outputTemplate = path.join(request.destination, `${filename}.%(ext)s`)
  const isAudio = request.downloadType === DownloadType.AUDIO_MP3

  const args: string[] = [
    '--no-warnings',
    '--no-playlist',
    '--progress',
    '--newline',
    '--retries', '3',
    '--fragment-retries', '3',
    '--extractor-args', 'youtube:player_client=android',
    '-o', outputTemplate,
  ]

  if (isAudio) {
    args.push(
      '-x',
      '--audio-format', 'mp3',
      '--audio-quality', `${request.audioQuality || '192'}k`
    )
  } else {
    const q = request.videoQuality || 'best'
    const fmt =
      q === 'best' ? 'bestvideo+bestaudio/best' :
      q === 'worst' ? 'worstvideo+worstaudio/worst' :
      `bestvideo[height<=${q.replace('p', '')}]+bestaudio/best`
    args.push('-f', fmt, '--merge-output-format', 'mkv')
  }

  args.push(request.url)

  onLog(`Downloading: ${info.title}`)
  onProgress({ status: DownloadStatus.PENDING, progress: 0.02, message: `Starting: ${info.title}` })

  wasCancelled = false

  return new Promise((resolve) => {
    const errLines: string[] = []
    activeProc = spawn(YT_DLP, args)

    activeProc.stdout.on('data', (d: Buffer) => {
      for (const line of d.toString().split('\n').filter(Boolean)) {
        onLog(line)
        const p = parseProgress(line)
        if (p) onProgress(p)
      }
    })

    activeProc.stderr.on('data', (d: Buffer) => {
      const msg = d.toString().trim()
      if (msg) {
        errLines.push(msg)
        onLog(msg)
      }
    })

    activeProc.on('error', (err) => {
      activeProc = null
      resolve([false, err.message])
    })

    activeProc.on('close', (code) => {
      activeProc = null
      if (wasCancelled) {
        onProgress({ status: DownloadStatus.FAILED, progress: 0, message: 'Cancelled' })
        resolve([false, 'Cancelled'])
        return
      }
      if (code === 0) {
        const ext = isAudio ? 'mp3' : 'mkv'
        const outFile = path.join(request.destination, `${filename}.${ext}`)
        onProgress({ status: DownloadStatus.COMPLETED, progress: 1.0, message: 'Done' })
        onLog('Done!')
        resolve([true, outFile])
      } else {
        const errMsg = cleanError(errLines.slice(-3).join(' ').trim() || 'Download failed')
        onProgress({ status: DownloadStatus.FAILED, progress: 0, message: errMsg })
        resolve([false, errMsg])
      }
    })
  })
}

function cleanError(raw: string): string {
  const s = raw.replace(/^ERROR:\s*/i, '').trim()
  if (/not available on this app/i.test(s))        return 'Not available'
  if (/private video|this video is private/i.test(s)) return 'Private video'
  if (/video unavailable|has been removed/i.test(s))  return 'Video unavailable'
  if (/age.?restrict/i.test(s))                     return 'Age-restricted'
  if (/copyright/i.test(s))                         return 'Blocked by copyright'
  if (/sign in/i.test(s))                           return 'Sign-in required'
  if (/postprocessing|merger|stream.*copy/i.test(s)) return 'Merge failed'
  if (/HTTP Error 403/i.test(s))                    return 'Access denied (403)'
  if (/HTTP Error 404/i.test(s))                    return 'Not found (404)'
  if (/no video formats/i.test(s))                  return 'No formats available'
  if (/unable to download|download failed/i.test(s)) return 'Download failed'
  // strip [extractor] VIDEO_ID: prefix
  return s.replace(/^\[[\w.:]+\]\s*[\w-]+:\s*/, '').split('\n')[0].trim()
}

function parseProgress(line: string): DownloadProgress | null {
  // [download]  45.6% of 3.12MiB at 1.23MiB/s ETA 00:02
  const m = line.match(/\[download\]\s+([\d.]+)%/)
  if (m) {
    const pct = parseFloat(m[1]) / 100
    return {
      status: DownloadStatus.DOWNLOADING,
      progress: 0.05 + pct * 0.88,
      message: line.replace('[download]', '').trim(),
    }
  }
  if (line.includes('[ffmpeg]') || line.includes('[ExtractAudio]') || line.includes('Merging')) {
    return { status: DownloadStatus.PROCESSING, progress: 0.95, message: 'Processing...' }
  }
  return null
}
