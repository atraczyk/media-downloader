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
- **FFmpeg** — required for MP3 conversion and video merging, must be on `PATH`

### yt-dlp binary (vendored in repo)

```bash
npm run update-ytdlp
```

This script downloads the latest `yt-dlp` binary for the current platform into `resources/`, verifies checksum, and updates:
- `resources/yt-dlp` or `resources/yt-dlp.exe` or `resources/yt-dlp_macos`
- `resources/SHA2-256SUMS`
- `resources/yt-dlp-version`

Commit those updated files when bumping `yt-dlp`.

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
- **Windows** — `dist/media-downloader-setup-*.exe` (NSIS)
- **macOS** — `dist/media-downloader-*.dmg`
- **Linux** — `dist/media-downloader-*.AppImage`

## Automation

GitHub Actions workflows:
- **CI** (`.github/workflows/ci.yml`)
  - Runs on pushes to `main` and pull requests
  - Executes unit tests, BDD tests, and build
- **Release** (`.github/workflows/release.yml`)
  - Runs on tag pushes matching `v*` or manual dispatch
  - Builds Windows/macOS/Linux distributables and publishes a GitHub release

Release tags should use `v` prefix (example: `v2.1.0`).

## Contributing

- Default branch is `main`.
- `main` is protected: PR review + CI are required for normal contributors.
- Keep changes small and focused.
- For behavior changes, update `.feature` scenarios first and follow the test workflow in **Testing (SDD/TDD)**.

## CLI

### Install globally

```bash
npm run build:cli
npm install -g .
```

Requires `yt-dlp` and `ffmpeg` on `PATH` (see [Requirements](#requirements)).

```bash
m-dl download "https://www.youtube.com/watch?v=…"

m-dl download <url> \
  -o ./my-downloads \   # output directory (default: downloads/)
  -t audio \            # audio | video  (default: audio)
  -q 320 \              # kbps for audio, or 720p/1080p for video (default: 192)
  --transcript          # also save transcript .txt
```

### Dev usage (no build needed)

```bash
npm run cli -- download "https://www.youtube.com/watch?v=…"
```

### Build the CLI

```bash
npm run build:cli          # compiles to out/cli/
node out/cli/cli/index.js download <url> [options]
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
