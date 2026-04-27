#!/usr/bin/env node
import { createHash } from 'crypto'
import { createWriteStream, mkdirSync, readFileSync, renameSync, rmSync, chmodSync, existsSync } from 'fs'
import { pipeline } from 'stream/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const RESOURCES = path.join(ROOT, 'resources')
const REPO = 'yt-dlp/yt-dlp'

const PLATFORM_BINARY = {
  win32:  'yt-dlp.exe',
  darwin: 'yt-dlp_macos',
  linux:  'yt-dlp',
}

async function fetchJson(url) {
  const res = await fetch(url, { headers: { 'User-Agent': 'mp3-dl-updater' } })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`)
  return res.json()
}

async function download(url, dest) {
  const res = await fetch(url, { headers: { 'User-Agent': 'mp3-dl-updater' } })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`)
  const tmp = dest + '.tmp'
  await pipeline(res.body, createWriteStream(tmp))
  renameSync(tmp, dest)
}

function sha256(filePath) {
  return createHash('sha256').update(readFileSync(filePath)).digest('hex')
}

function verifySums(sumsText, binaryName, binaryPath) {
  const entry = sumsText.split('\n').find(l => l.trimEnd().endsWith(binaryName))
  if (!entry) throw new Error(`No checksum entry found for ${binaryName}`)
  const expected = entry.split(/\s+/)[0].toLowerCase()
  const actual = sha256(binaryPath)
  if (actual !== expected) {
    throw new Error(`Checksum mismatch for ${binaryName}\n  expected: ${expected}\n  got:      ${actual}`)
  }
  return actual
}

async function main() {
  const binaryName = PLATFORM_BINARY[process.platform]
  if (!binaryName) throw new Error(`Unsupported platform: ${process.platform}`)

  mkdirSync(RESOURCES, { recursive: true })

  console.log('Fetching latest yt-dlp release...')
  const release = await fetchJson(`https://api.github.com/repos/${REPO}/releases/latest`)
  const version = release.tag_name
  console.log(`Version: ${version}`)

  const assetUrl = (name) => {
    const a = release.assets.find(a => a.name === name)
    if (!a) throw new Error(`Asset not in release: ${name}`)
    return a.browser_download_url
  }

  const binaryDest = path.join(RESOURCES, binaryName)
  const sumsDest   = path.join(RESOURCES, 'SHA2-256SUMS')

  process.stdout.write(`Downloading ${binaryName}... `)
  await download(assetUrl(binaryName), binaryDest)
  console.log('done')

  process.stdout.write('Downloading SHA2-256SUMS... ')
  await download(assetUrl('SHA2-256SUMS'), sumsDest)
  console.log('done')

  process.stdout.write('Verifying checksum... ')
  const sumsText = readFileSync(sumsDest, 'utf-8')
  const hash = verifySums(sumsText, binaryName, binaryDest)
  console.log(`ok (${hash.slice(0, 16)}…)`)

  if (process.platform !== 'win32') chmodSync(binaryDest, 0o755)

  // Record version for reference
  const { writeFileSync } = await import('fs')
  writeFileSync(path.join(RESOURCES, 'yt-dlp-version'), version, 'utf-8')

  console.log(`\n✓ yt-dlp ${version} vendored to resources/${binaryName}`)
}

main().catch(err => { console.error('\nError:', err.message); process.exit(1) })
