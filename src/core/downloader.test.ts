import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { parseOutputPath, resolveOutputFilePath } from './downloader.js'

test('parseOutputPath parses download destination line', () => {
  const line = '[download] Destination: C:\\downloads\\Track Name.webm'
  assert.equal(parseOutputPath(line), 'C:\\downloads\\Track Name.webm')
})

test('parseOutputPath parses extract audio destination line', () => {
  const line = '[ExtractAudio] Destination: C:\\downloads\\Track Name.mp3'
  assert.equal(parseOutputPath(line), 'C:\\downloads\\Track Name.mp3')
})

test('parseOutputPath parses merger output path with quotes', () => {
  const line = '[Merger] Merging formats into "C:\\downloads\\Track Name.mkv"'
  assert.equal(parseOutputPath(line), 'C:\\downloads\\Track Name.mkv')
})

test('parseOutputPath returns null for unrelated line', () => {
  assert.equal(parseOutputPath('[download] 45.0% of 3.12MiB at 1.23MiB/s ETA 00:02'), null)
})

test('resolveOutputFilePath uses detected path when it exists', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-test-'))
  try {
    const actualOutput = path.join(tempDir, 'actual.webm')
    fs.writeFileSync(actualOutput, 'x')
    const resolved = resolveOutputFilePath({
      destination: tempDir,
      filename: 'fallback',
      isAudio: false,
      detectedOutputPath: actualOutput,
    })
    assert.equal(resolved, actualOutput)
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true })
  }
})

test('resolveOutputFilePath falls back when detected path is missing', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-test-'))
  try {
    const resolved = resolveOutputFilePath({
      destination: tempDir,
      filename: 'fallback',
      isAudio: true,
      detectedOutputPath: path.join(tempDir, 'missing.mp3'),
    })
    assert.equal(resolved, path.join(tempDir, 'fallback.mp3'))
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true })
  }
})
