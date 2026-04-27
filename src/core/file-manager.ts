import fs from 'fs'
import path from 'path'

export function sanitizeFilename(name: string): string {
  return (
    name
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, '')
      .replace(/[\u{10000}-\u{10FFFF}]/gu, '')
      .replace(/[^\w\s\-.,()[\]]/gu, '')
      .replace(/\s+/g, '_')
      .replace(/^[_.\-]+|[_.\-]+$/g, '')
      .slice(0, 200) || 'download'
  )
}

export async function saveTranscript(
  text: string,
  mediaFilename: string,
  destination: string
): Promise<string | null> {
  try {
    const base = path.basename(mediaFilename, path.extname(mediaFilename))
    const filePath = path.join(destination, `${base}_transcript.txt`)
    await fs.promises.writeFile(filePath, text, 'utf-8')
    return filePath
  } catch {
    return null
  }
}

export async function ensureDirectory(dirPath: string): Promise<[boolean, string | null]> {
  try {
    await fs.promises.mkdir(dirPath, { recursive: true })
    return [true, null]
  } catch (err: any) {
    return [false, err.message]
  }
}
