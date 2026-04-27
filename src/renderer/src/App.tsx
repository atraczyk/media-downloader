import { useState, useEffect, useRef } from 'react'

type DownloadType = 'audio' | 'video'

interface ProgressData {
  status: string
  progress: number
  message: string
}

interface TranscriptData {
  text?: string
  error?: string
}

interface CompleteData {
  success: boolean
  message: string
  filename?: string
}

export default function App() {
  const [url, setUrl] = useState('')
  const [urlTitle, setUrlTitle] = useState('')
  const [urlError, setUrlError] = useState('')
  const [urlPending, setUrlPending] = useState(false)

  const [dlType, setDlType] = useState<DownloadType>('audio')
  const [audioQuality, setAudioQuality] = useState('192')
  const [videoQuality, setVideoQuality] = useState('best')
  const [destination, setDestination] = useState('downloads')
  const [transcriptOn, setTranscriptOn] = useState(false)

  const [downloading, setDownloading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressStatus, setProgressStatus] = useState('')
  const [progressMsg, setProgressMsg] = useState('')

  const [logs, setLogs] = useState<string[]>([])
  const [transcript, setTranscript] = useState<TranscriptData | null>(null)
  const [showTranscript, setShowTranscript] = useState(false)

  const logsRef = useRef<HTMLDivElement>(null)
  const urlTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Register IPC listeners once on mount
  useEffect(() => {
    const api = window.electronAPI

    api.onProgress((d: ProgressData) => {
      setProgress(d.progress)
      setProgressStatus(d.status)
      setProgressMsg(d.message)
    })

    api.onTranscript((d: TranscriptData) => setTranscript(d))

    api.onComplete((d: CompleteData) => {
      setDownloading(false)
      appendLog(d.success
        ? `✓ Saved: ${d.filename ?? ''}`
        : `✗ Failed: ${d.message}`
      )
    })

    api.onLog((msg: string) => appendLog(msg))

    return () => {
      ;['download:progress', 'download:transcript', 'download:complete', 'download:log']
        .forEach(api.removeAllListeners)
    }
  }, [])

  // Auto-scroll log box
  useEffect(() => {
    if (logsRef.current) logsRef.current.scrollTop = logsRef.current.scrollHeight
  }, [logs])

  function appendLog(msg: string) {
    const ts = new Date().toLocaleTimeString()
    setLogs(prev => [...prev.slice(-199), `[${ts}] ${msg}`])
  }

  function handleUrlChange(val: string) {
    setUrl(val)
    setUrlTitle('')
    setUrlError('')
    if (urlTimer.current) clearTimeout(urlTimer.current)
    if (!val.trim()) return
    urlTimer.current = setTimeout(() => validateUrl(val), 600)
  }

  async function validateUrl(val: string) {
    setUrlPending(true)
    try {
      const res = await window.electronAPI.validateUrl(val)
      if (res.valid) {
        setUrlTitle(res.title ?? '')
        setUrlError('')
      } else {
        setUrlError(res.error ?? 'Invalid URL')
        setUrlTitle('')
      }
    } catch {
      setUrlError('Validation failed')
    } finally {
      setUrlPending(false)
    }
  }

  async function browseFolder() {
    const res = await window.electronAPI.browseFolder()
    if (res.success && res.path) setDestination(res.path)
  }

  async function startDownload() {
    if (downloading || !url.trim()) return
    setDownloading(true)
    setProgress(0)
    setProgressMsg('')
    setProgressStatus('')
    setLogs([])
    setTranscript(null)
    setShowTranscript(false)

    const res = await window.electronAPI.startDownload({
      url: url.trim(),
      destination: destination.trim() || 'downloads',
      downloadType: dlType,
      audioQuality,
      videoQuality,
      transcriptEnabled: transcriptOn,
    })

    if (!res.success) {
      setDownloading(false)
      appendLog(`✗ ${res.error ?? 'Failed to start'}`)
    }
  }

  const btnLabel = downloading
    ? 'Downloading…'
    : dlType === 'audio' ? '↓ Download MP3' : '↓ Download Video'

  const showProgress = downloading
    || progressStatus === 'completed'
    || progressStatus === 'failed'

  return (
    <div className="app">
      <header className="app-header">
        <h1>Media Downloader</h1>
        <p>Download audio and video from YouTube</p>
      </header>

      <div className="content">
        {/* URL */}
        <div className="card">
          <p className="card-label">URL</p>
          <input
            className="input"
            type="url"
            placeholder="https://www.youtube.com/watch?v=…"
            value={url}
            onChange={e => handleUrlChange(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && startDownload()}
            disabled={downloading}
          />
          {urlPending && <p className="hint hint-wait">Checking…</p>}
          {urlTitle && !urlPending && <p className="hint hint-ok">✓ {urlTitle}</p>}
          {urlError && !urlPending && <p className="hint hint-err">✗ {urlError}</p>}
        </div>

        {/* Options */}
        <div className="card">
          <p className="card-label">Options</p>

          <div className="radio-group">
            {(['audio', 'video'] as DownloadType[]).map(t => (
              <label key={t} className="radio-item">
                <input
                  type="radio"
                  name="dlType"
                  value={t}
                  checked={dlType === t}
                  onChange={() => setDlType(t)}
                  disabled={downloading}
                />
                {t === 'audio' ? 'Audio (MP3)' : 'Video'}
              </label>
            ))}
          </div>

          {dlType === 'audio' && (
            <div className="option-row">
              <span style={{ color: '#555', minWidth: 60 }}>Quality</span>
              <select
                className="select"
                value={audioQuality}
                onChange={e => setAudioQuality(e.target.value)}
                disabled={downloading}
              >
                {['128', '192', '256', '320'].map(q => (
                  <option key={q} value={q}>{q} kbps</option>
                ))}
              </select>
            </div>
          )}

          {dlType === 'video' && (
            <div className="option-row">
              <span style={{ color: '#555', minWidth: 60 }}>Quality</span>
              <select
                className="select"
                value={videoQuality}
                onChange={e => setVideoQuality(e.target.value)}
                disabled={downloading}
              >
                {[['best', 'Best available'], ['1080p', '1080p'], ['720p', '720p'], ['480p', '480p'], ['360p', '360p']].map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
          )}

          <label className="checkbox-item" style={{ marginTop: 4 }}>
            <input
              type="checkbox"
              checked={transcriptOn}
              onChange={e => setTranscriptOn(e.target.checked)}
              disabled={downloading}
            />
            Download transcript (if available)
          </label>
        </div>

        {/* Destination */}
        <div className="card">
          <p className="card-label">Destination</p>
          <div className="row">
            <input
              className="input"
              type="text"
              value={destination}
              onChange={e => setDestination(e.target.value)}
              disabled={downloading}
            />
            <button className="btn btn-secondary" onClick={browseFolder} disabled={downloading}>
              Browse
            </button>
          </div>
        </div>

        {/* Download + Progress */}
        <div className="card">
          <button
            className="btn btn-primary btn-full"
            onClick={startDownload}
            disabled={downloading || !url.trim()}
          >
            {btnLabel}
          </button>

          {showProgress && (
            <div className="progress-wrap">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${Math.round(progress * 100)}%` }}
                />
              </div>
              <p className={`progress-msg s-${progressStatus}`}>{progressMsg}</p>
            </div>
          )}
        </div>

        {/* Transcript */}
        {transcript && (
          <div className="card">
            <div className="card-header">
              <p className="card-label">Transcript</p>
              {transcript.text && (
                <button className="btn btn-ghost" onClick={() => setShowTranscript(v => !v)}>
                  {showTranscript ? 'Hide' : 'Show'}
                </button>
              )}
            </div>
            {transcript.error && (
              <p className="hint hint-err">{transcript.error}</p>
            )}
            {showTranscript && transcript.text && (
              <div className="transcript-box">{transcript.text}</div>
            )}
          </div>
        )}

        {/* Logs */}
        <div className="card">
          <div className="card-header">
            <p className="card-label">Log</p>
            <button className="btn btn-ghost" onClick={() => setLogs([])}>Clear</button>
          </div>
          <div className="log-box" ref={logsRef}>
            {logs.length === 0
              ? <div className="log-line" style={{ color: '#666' }}>Ready.</div>
              : logs.map((l, i) => <div key={i} className="log-line">{l}</div>)
            }
          </div>
        </div>
      </div>
    </div>
  )
}
