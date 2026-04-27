export {}

interface ValidateResult {
  valid: boolean
  title?: string
  duration?: number
  uploader?: string
  error?: string
}

interface BrowseResult {
  success: boolean
  path?: string
}

interface StartResult {
  success: boolean
  error?: string
}

interface ProgressData {
  status: string
  progress: number
  message: string
  speed?: number
}

interface TranscriptData {
  text?: string
  cleanText?: string
  error?: string
}

interface CompleteData {
  success: boolean
  message: string
  filename?: string
}

declare global {
  interface Window {
    electronAPI: {
      validateUrl: (url: string) => Promise<ValidateResult>
      browseFolder: () => Promise<BrowseResult>
      startDownload: (request: unknown) => Promise<StartResult>
      getStatus: () => Promise<{ isDownloading: boolean }>
      onProgress: (cb: (data: ProgressData) => void) => void
      onTranscript: (cb: (data: TranscriptData) => void) => void
      onComplete: (cb: (data: CompleteData) => void) => void
      onLog: (cb: (msg: string) => void) => void
      removeAllListeners: (channel: string) => void
      minimize: () => Promise<void>
      maximize: () => Promise<void>
      close: () => Promise<void>
      isMaximized: () => Promise<boolean>
      onMaximizeChanged: (cb: (maximized: boolean) => void) => void
    }
  }
}
