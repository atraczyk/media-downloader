#!/usr/bin/env tsx
import { Command } from 'commander'
import path from 'path'
import { getMediaInfo, downloadMedia } from '../core/downloader.js'
import { fetchTranscript } from '../core/transcript.js'
import { saveTranscript, ensureDirectory } from '../core/file-manager.js'
import { DownloadType } from '../core/types.js'

const program = new Command()

program
  .name('mp3-dl')
  .description('Download audio and video from YouTube')
  .version('2.0.0')

program
  .command('download <url>')
  .description('Download media from a YouTube URL')
  .option('-o, --output <dir>', 'Output directory', 'downloads')
  .option('-t, --type <type>', 'Download type: audio or video', 'audio')
  .option('-q, --quality <quality>', 'Audio kbps (128/192/256/320) or video res (720p/1080p)', '192')
  .option('--transcript', 'Also download transcript', false)
  .option('--no-progress', 'Suppress inline progress output')
  .action(async (url: string, opts: {
    output: string
    type: string
    quality: string
    transcript: boolean
    progress: boolean
  }) => {
    const outputDir = path.resolve(opts.output)

    console.log(`Fetching info: ${url}`)
    const [info, infoErr] = await getMediaInfo(url)
    if (!info) { console.error(`Error: ${infoErr}`); process.exit(1) }

    console.log(`Title:    ${info.title}`)
    if (info.uploader) console.log(`Channel:  ${info.uploader}`)
    if (info.duration) {
      const m = Math.floor(info.duration / 60)
      const s = info.duration % 60
      console.log(`Duration: ${m}:${String(s).padStart(2, '0')}`)
    }
    console.log(`Output:   ${outputDir}`)

    const [dirOk, dirErr] = await ensureDirectory(outputDir)
    if (!dirOk) { console.error(`Cannot create dir: ${dirErr}`); process.exit(1) }

    if (opts.transcript) {
      process.stdout.write('Fetching transcript…')
      const result = await fetchTranscript(url)
      if (result.text) {
        const saved = await saveTranscript(result.text, info.sanitizedFilename, outputDir)
        process.stdout.write(` saved: ${saved}\n`)
      } else {
        process.stdout.write(` unavailable: ${result.error}\n`)
      }
    }

    const dlType = opts.type === 'video' ? DownloadType.VIDEO_WEBM : DownloadType.AUDIO_MP3

    const [success, result] = await downloadMedia(
      {
        url,
        destination: outputDir,
        downloadType: dlType,
        audioQuality: dlType === DownloadType.AUDIO_MP3 ? opts.quality : undefined,
        videoQuality: dlType === DownloadType.VIDEO_WEBM ? opts.quality : undefined,
        transcriptEnabled: opts.transcript,
      },
      (p) => {
        if (opts.progress && p.message) {
          process.stdout.write(`\r${p.message.slice(0, 72).padEnd(72)}`)
        }
      },
      (msg) => {
        if (!msg.startsWith('[download]')) console.log(msg)
      }
    )

    if (opts.progress) process.stdout.write('\n')

    if (success) {
      console.log(`\n✓ ${result}`)
    } else {
      console.error(`\n✗ ${result}`)
      process.exit(1)
    }
  })

program.parse()
