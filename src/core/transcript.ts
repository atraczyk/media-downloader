import { TranscriptResult } from './types.js'

function extractVideoId(url: string): string | null {
  const patterns = [
    /(?:v=)([\w-]{11})/,
    /youtu\.be\/([\w-]{11})/,
    /embed\/([\w-]{11})/,
    /\/v\/([\w-]{11})/,
  ]
  for (const pattern of patterns) {
    const m = url.match(pattern)
    if (m) return m[1]
  }
  return null
}

export async function fetchTranscript(url: string): Promise<TranscriptResult> {
  const videoId = extractVideoId(url)
  if (!videoId) return { error: 'Could not extract video ID from URL' }

  try {
    // Dynamic import handles both CJS and ESM builds of youtube-transcript
    const { YoutubeTranscript } = await import('youtube-transcript')
    const entries = await YoutubeTranscript.fetchTranscript(videoId)

    const text = entries
      .map((e: any) => {
        const t = Math.floor((e.offset ?? e.start ?? 0) / 1000)
        const mm = String(Math.floor(t / 60)).padStart(2, '0')
        const ss = String(t % 60).padStart(2, '0')
        return `[${mm}:${ss}] ${(e.text ?? '').replace(/\n/g, ' ').trim()}`
      })
      .join('\n')

    const cleanText = entries
      .map((e: any) => (e.text ?? '').replace(/\n/g, ' ').trim())
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim()

    return { text, cleanText }
  } catch (err: any) {
    return { error: err.message || 'Transcript not available' }
  }
}
