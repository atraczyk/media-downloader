# Media Downloader

Download audio (MP3) and video from YouTube — desktop GUI and CLI in one package, built with TypeScript + Electron + React.

## Features

- Download audio as MP3 at 128/192/256/320 kbps
- Download video (best, 1080p, 720p, 480p, 360p)
- Real-time progress bar and log output
- Optional transcript download (timestamped .txt)
- URL validation with title preview before downloading
- Standalone CLI sharing the same core logic

## Requirements

- **Node.js** 18+
- **yt-dlp** — must be on `PATH` (or place `yt-dlp.exe` / `yt-dlp` beside the app)
- **FFmpeg** — required for MP3 conversion and video merging, must be on `PATH`

### Installing yt-dlp

```bash
# Windows (winget)
winget install yt-dlp

# macOS
brew install yt-dlp

# Linux
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

### Installing FFmpeg

```bash
# Windows (winget)
winget install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg
```

## Development

```bash
npm install
npm run dev       # Electron app with hot reload
```

## Testing (SDD/TDD)

This repo uses:
- **Cucumber-style Gherkin features** (`features/*.feature`)
- **Playwright-BDD** to turn scenarios into Playwright tests
- **Node unit tests** for lower-level logic

```bash
npx playwright install chromium   # one-time browser install
npm run test:unit                 # fast unit tests
npm run test:bdd                  # feature-level BDD tests
```

Feature-first workflow:
1. Add or update a `.feature` scenario for behavior you want.
2. Run `npm run test:bdd` and watch it fail (red).
3. Implement app code + step definitions until tests pass (green).
4. Refactor while keeping both unit and BDD tests green.

## Build

```bash
npm run build     # Compile to out/
npm run package   # Build installer for current OS
npm run package:win
npm run package:mac
npm run package:linux
```

Outputs:
- **Windows** — `dist/Media Downloader Setup *.exe` (NSIS)
- **macOS** — `dist/Media Downloader-*.dmg`
- **Linux** — `dist/Media Downloader-*.AppImage`

## CLI

```bash
# Dev (tsx, no build needed)
npm run cli -- download "https://www.youtube.com/watch?v=…"

# Options
npm run cli -- download <url> \
  -o ./my-downloads \   # output directory (default: downloads/)
  -t audio \            # audio | video  (default: audio)
  -q 320 \              # kbps for audio, or 720p/1080p for video (default: 192)
  --transcript          # also save transcript .txt

# After build, call directly
node out/cli/index.js download <url> [options]
```

## Project Structure

```
src/
  core/
    types.ts          # shared enums and interfaces
    downloader.ts     # yt-dlp subprocess wrapper
    transcript.ts     # youtube-transcript fetcher
    file-manager.ts   # sanitize filenames, save files
  main/
    index.ts          # Electron main process, BrowserWindow
    ipc-handlers.ts   # IPC bridge (validate, browse, start, status)
  preload/
    index.ts          # contextBridge → window.electronAPI
  renderer/
    index.html
    src/
      main.tsx
      App.tsx         # single-page UI
      App.css
      env.d.ts        # window.electronAPI type declarations
  cli/
    index.ts          # commander CLI entry point
package.json
electron.vite.config.ts
tsconfig.json / tsconfig.node.json / tsconfig.web.json
```

## Troubleshooting

**`yt-dlp` not found** — ensure it is installed and on `PATH`. Restart your terminal after installation.

**FFmpeg not found** — same as above. Required for `-x`/`--audio-format mp3` and `--merge-output-format`.

**Transcript unavailable** — not all videos have auto-generated or manual captions. The app will report this without failing the download.

**Video download produces `.webm`** — this is expected; yt-dlp merges the best audio+video streams into WebM by default.
