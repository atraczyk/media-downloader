export enum DownloadType {
  AUDIO_MP3 = 'audio',
  VIDEO_WEBM = 'video',
}

export enum DownloadStatus {
  PENDING = 'pending',
  DOWNLOADING = 'downloading',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface DownloadRequest {
  url: string
  destination: string
  downloadType: DownloadType
  audioQuality?: string
  videoQuality?: string
  transcriptEnabled?: boolean
}

export interface DownloadProgress {
  status: DownloadStatus
  progress: number  // 0.0–1.0
  message: string
  speed?: number    // MB/s
}

export interface MediaInfo {
  title: string
  duration?: number
  uploader?: string
  sanitizedFilename: string
}

export interface TranscriptResult {
  text?: string
  cleanText?: string
  error?: string
}

export interface DownloadResult {
  success: boolean
  message: string
  filename?: string
}
