import { useState, useEffect, useLayoutEffect, useRef } from 'react'

type DownloadType = 'audio' | 'video'

interface ProgressData { status: string; progress: number; message: string }
interface TranscriptData { text?: string; error?: string }
interface CompleteData { success: boolean; message: string; filename?: string }

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
  const [lastFile, setLastFile] = useState<string | null>(null)

  const [logs, setLogs] = useState<string[]>([])
  const [transcript, setTranscript] = useState<TranscriptData | null>(null)
  const [showTranscript, setShowTranscript] = useState(false)

  const [theme, setTheme] = useState<'dark' | 'light' | 'system'>(
    () => (localStorage.getItem('theme') as 'dark' | 'light' | 'system') || 'dark'
  )

  const logsRef = useRef<HTMLDivElement>(null)
  const urlTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const urlSeq = useRef(0)

  useLayoutEffect(() => {
    function apply(t: 'dark' | 'light' | 'system') {
      const resolved = t === 'system'
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
        : t
      document.documentElement.setAttribute('data-theme', resolved)
    }
    apply(theme)
    localStorage.setItem('theme', theme)
    if (theme !== 'system') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => apply('system')
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [theme])

  function cycleTheme() {
    setTheme(t => t === 'dark' ? 'light' : t === 'light' ? 'system' : 'dark')
  }

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
      if (d.success && d.filename) setLastFile(d.filename)
      const label = d.success
        ? `✓ Saved: ${d.filename?.replace(/.*[\\/]/, '') ?? 'file'}`
        : `✗ ${d.message}`
      appendLog(label)
    })

    api.onLog((msg: string) => appendLog(msg))

    return () => {
      ;['download:progress', 'download:transcript', 'download:complete', 'download:log']
        .forEach(api.removeAllListeners)
    }
  }, [])

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
    if (!val.trim()) { setUrlPending(false); return }
    setUrlPending(true)
    urlTimer.current = setTimeout(() => validateUrl(val), 600)
  }

  async function validateUrl(val: string) {
    const seq = ++urlSeq.current
    try {
      const res = await window.electronAPI.validateUrl(val)
      if (seq !== urlSeq.current) return
      if (res.valid) {
        setUrlTitle(res.title ?? '')
        setUrlError('')
        if (res.isAudioOnly !== undefined) setDlType(res.isAudioOnly ? 'audio' : 'video')
      } else {
        setUrlError(res.error ?? 'Invalid URL')
        setUrlTitle('')
      }
    } catch {
      if (seq !== urlSeq.current) return
      setUrlError('Validation failed')
    } finally {
      if (seq === urlSeq.current) setUrlPending(false)
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
    setLastFile(null)
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

  const showProgress = downloading || progressStatus === 'completed' || progressStatus === 'failed'

  const urlStatusClass = urlPending ? 'hint-wait' : urlTitle ? 'hint-ok' : urlError ? 'hint-err' : ''
  const urlStatusText  = urlPending ? 'Checking…' : urlTitle ? `✓ ${urlTitle}` : urlError ? `✗ ${urlError}` : ''

  return (
    <div className="app">
      <header className="titlebar">
        <span className="titlebar-title">Media Downloader</span>
        <div className="titlebar-controls">
          <button className="wc-btn" onClick={cycleTheme} title={`Theme: ${theme}`} style={{ fontSize: 14 }}>
            {theme === 'dark' ? '●' : theme === 'light' ? '○' : '◐'}
          </button>
          <button className="wc-btn" onClick={() => window.electronAPI.minimize()}>
            <svg width="10" height="1" viewBox="0 0 10 1"><rect width="10" height="1" fill="currentColor"/></svg>
          </button>
          <button className="wc-btn wc-close" onClick={() => window.electronAPI.close()}>
            <svg width="10" height="10" viewBox="0 0 10 10">
              <line x1="0" y1="0" x2="10" y2="10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <line x1="10" y1="0" x2="0" y2="10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
      </header>

      <div className="content">

        {/* URL */}
        <div className="section">
          <div className="section-header">
            <span className="section-label">URL</span>
            <span className={`url-status ${urlStatusClass}`}>{urlStatusText}</span>
          </div>
          <input
            className="input"
            type="url"
            placeholder="https://www.youtube.com/watch?v=…"
            value={url}
            onChange={e => handleUrlChange(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && startDownload()}
            disabled={downloading}
          />
        </div>

        {/* Format + Options */}
        <div className="section">
          <span className="section-label">Format</span>
          <div className="format-row" style={{ marginTop: 8 }}>
            <div className="seg-control">
              {(['audio', 'video'] as DownloadType[]).map(t => (
                <button
                  key={t}
                  className={`seg-btn ${dlType === t ? 'active' : ''}`}
                  onClick={() => setDlType(t)}
                  disabled={downloading}
                >
                  {t === 'audio' ? 'Audio · MP3' : 'Video'}
                </button>
              ))}
            </div>
            <div className="quality-group">
              <span className="quality-label">Quality</span>
              <select
                className="select"
                value={dlType === 'audio' ? audioQuality : videoQuality}
                onChange={e => dlType === 'audio' ? setAudioQuality(e.target.value) : setVideoQuality(e.target.value)}
                disabled={downloading}
              >
                {dlType === 'audio'
                  ? ['128', '192', '256', '320'].map(q => <option key={q} value={q}>{q} kbps</option>)
                  : [['best', 'Best'], ['1080p', '1080p'], ['720p', '720p'], ['480p', '480p'], ['360p', '360p']].map(([v, l]) => (
                      <option key={v} value={v}>{l}</option>
                    ))
                }
              </select>
            </div>
          </div>
          <label className="toggle-row">
            <input
              type="checkbox"
              checked={transcriptOn}
              onChange={e => setTranscriptOn(e.target.checked)}
              disabled={downloading}
            />
            Download transcript
          </label>
        </div>

        {/* Destination */}
        <div className="section">
          <div className="section-header">
            <span className="section-label">Destination</span>
          </div>
          <div className="dest-row">
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
        <div className="section">
          <button
            className={`btn btn-full ${downloading ? 'btn-cancel' : 'btn-primary'}`}
            onClick={downloading ? () => window.electronAPI.cancelDownload() : startDownload}
            disabled={!downloading && !url.trim()}
          >
            {downloading ? '✕  Cancel' : dlType === 'audio' ? '↓  Download MP3' : '↓  Download Video'}
          </button>
          <div className="progress-wrap">
            <div className={`progress-bar${showProgress ? '' : ' progress-bar--idle'}`}>
              <div className="progress-fill" style={{ width: `${showProgress ? Math.round(progress * 100) : 0}%` }} />
            </div>
            <div className="progress-footer">
              <p className={`progress-msg${showProgress ? ` s-${progressStatus}` : ' s-idle'}`}>
                {showProgress ? progressMsg : 'Ready'}
              </p>
              {lastFile && (
                <button className="btn btn-ghost" onClick={() => window.electronAPI.showItem(lastFile)}>
                  Show in folder
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Transcript */}
        {transcript && (
          <div className="section">
            <div className="section-header">
              <span className="section-label">Transcript</span>
              {transcript.text && (
                <button className="btn btn-ghost" onClick={() => setShowTranscript(v => !v)}>
                  {showTranscript ? 'Hide' : 'Show'}
                </button>
              )}
            </div>
            {transcript.error && <p className="hint hint-err">{transcript.error}</p>}
            {showTranscript && transcript.text && (
              <div className="transcript-box">{transcript.text}</div>
            )}
          </div>
        )}

        {/* Log */}
        <div className="section section-log">
          <div className="section-header">
            <span className="section-label">Log</span>
            <button className="btn btn-ghost" onClick={() => setLogs([])}>Clear</button>
          </div>
          <div className="log-box" ref={logsRef}>
            {logs.length === 0
              ? <div className="log-line log-line--ready">ready.</div>
              : logs.map((l, i) => <div key={i} className="log-line">{l}</div>)
            }
          </div>
        </div>

      </div>
    </div>
  )
}
