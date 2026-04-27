import { spawn } from 'child_process'
import path from 'path'
import { DownloadRequest, DownloadProgress, DownloadStatus, DownloadType, MediaInfo } from './types.js'
import { sanitizeFilename } from './file-manager.js'

type ProgressCallback = (progress: DownloadProgress) => void
type LogCallback = (message: string) => void

// On Windows, try yt-dlp.exe first, fall back to yt-dlp
const YT_DLP = process.platform === 'win32' ? 'yt-dlp.exe' : 'yt-dlp'

export async function getMediaInfo(url: string): Promise<[MediaInfo | null, string | null]> {
  return new Promise((resolve) => {
    const chunks: string[] = []
    const errChunks: string[] = []
    const proc = spawn(YT_DLP, ['--dump-json', '--no-playlist', '--no-warnings', url])

    proc.stdout.on('data', (d: Buffer) => chunks.push(d.toString()))
    proc.stderr.on('data', (d: Buffer) => errChunks.push(d.toString()))

    proc.on('error', (err) => resolve([null, err.message]))
    proc.on('close', (code) => {
      if (code !== 0) {
        const msg = errChunks.join('').trim() || 'Failed to fetch video info'
        resolve([null, msg.split('\n').slice(-2).join(' ')])
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
          },
          null,
        ])
      } catch {
        resolve([null, 'Failed to parse video info'])
      }
    })
  })
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
    args.push('-f', fmt, '--merge-output-format', 'webm')
  }

  args.push(request.url)

  onLog(`Downloading: ${info.title}`)
  onProgress({ status: DownloadStatus.PENDING, progress: 0.02, message: `Starting: ${info.title}` })

  return new Promise((resolve) => {
    const errLines: string[] = []
    const proc = spawn(YT_DLP, args)

    proc.stdout.on('data', (d: Buffer) => {
      for (const line of d.toString().split('\n').filter(Boolean)) {
        onLog(line)
        const p = parseProgress(line)
        if (p) onProgress(p)
      }
    })

    proc.stderr.on('data', (d: Buffer) => {
      const msg = d.toString().trim()
      if (msg) {
        errLines.push(msg)
        onLog(msg)
      }
    })

    proc.on('error', (err) => resolve([false, err.message]))

    proc.on('close', (code) => {
      if (code === 0) {
        const ext = isAudio ? 'mp3' : 'webm'
        const outFile = path.join(request.destination, `${filename}.${ext}`)
        onProgress({ status: DownloadStatus.COMPLETED, progress: 1.0, message: 'Download complete!' })
        onLog('Done!')
        resolve([true, outFile])
      } else {
        const errMsg = errLines.slice(-3).join(' ').trim() || 'Download failed'
        onProgress({ status: DownloadStatus.FAILED, progress: 0, message: errMsg })
        resolve([false, errMsg])
      }
    })
  })
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
