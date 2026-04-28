import { expect } from '@playwright/test'
import { createBdd } from 'playwright-bdd'

const { Given, When, Then } = createBdd()

function urlInput(page: any) {
  return page.getByPlaceholder('https://www.youtube.com/watch?v=…')
}

function downloadButton(page: any) {
  return page.getByRole('button', { name: /Download MP3|Download Video/i })
}

function destinationInput(page: any) {
  return page.locator('.dest-row input')
}

function qualitySelect(page: any) {
  return page.locator('.quality-group select')
}

async function readMock(page: any, expr: string, ...args: any[]) {
  return page.evaluate(
    ({ expr, args }: { expr: string; args: any[] }) => {
      const fn = new Function('window', 'args', `return ${expr}`)
      return fn(window, args)
    },
    { expr, args }
  )
}

Given('the media downloader app is open', async ({ page }) => {
  await page.addInitScript(() => {
    const listeners: Record<string, Array<(data: unknown) => void>> = {
      'download:progress': [],
      'download:transcript': [],
      'download:complete': [],
      'download:log': [],
      'window:maximize-changed': [],
    }

    const state: Record<string, unknown> = {
      validateResponses: {},
      browseFolderResult: { success: false },
      startDownloadResult: { success: true },
      startRequests: [],
      showItemCalls: [],
      cancelCount: 0,
    }

    const api = {
      validateUrl: async (url: string) => {
        const map = state.validateResponses as Record<string, unknown>
        return (map[url] as unknown) ?? { valid: false, error: 'Invalid URL' }
      },
      browseFolder: async () => state.browseFolderResult,
      startDownload: async (request: unknown) => {
        ;(state.startRequests as unknown[]).push(request)
        return state.startDownloadResult
      },
      getStatus: async () => ({ isDownloading: false }),
      onProgress: (cb: (data: unknown) => void) => listeners['download:progress'].push(cb),
      onTranscript: (cb: (data: unknown) => void) => listeners['download:transcript'].push(cb),
      onComplete: (cb: (data: unknown) => void) => listeners['download:complete'].push(cb),
      onLog: (cb: (data: unknown) => void) => listeners['download:log'].push(cb),
      removeAllListeners: (channel: string) => { listeners[channel] = [] },
      cancelDownload: async () => { state.cancelCount = (state.cancelCount as number) + 1 },
      getDefaultDest: async () => 'downloads',
      getAppVersion: async () => '2.0.0-test',
      resolvePath: async (p: string) => p,
      showItem: async (filePath: string) => { (state.showItemCalls as string[]).push(filePath) },
      minimize: async () => {},
      maximize: async () => {},
      close: async () => {},
      isMaximized: async () => false,
      onMaximizeChanged: (cb: (maximized: boolean) => void) =>
        listeners['window:maximize-changed'].push(cb),
    }

    ;(window as any).electronAPI = api
    ;(window as any).__bddMock = {
      setValidateResponse(url: string, response: unknown) {
        ;(state.validateResponses as Record<string, unknown>)[url] = response
      },
      setBrowseFolderResult(result: unknown) {
        state.browseFolderResult = result
      },
      setStartDownloadResult(result: unknown) {
        state.startDownloadResult = result
      },
      emitProgress(data: unknown) {
        for (const cb of listeners['download:progress']) cb(data)
      },
      emitTranscript(data: unknown) {
        for (const cb of listeners['download:transcript']) cb(data)
      },
      emitComplete(data: unknown) {
        for (const cb of listeners['download:complete']) cb(data)
      },
      emitLog(msg: string) {
        for (const cb of listeners['download:log']) cb(msg)
      },
      getLastStartRequest() {
        const reqs = state.startRequests as unknown[]
        return reqs[reqs.length - 1] ?? null
      },
      getShowItemCalls() {
        return [...(state.showItemCalls as string[])]
      },
      getCancelCount() {
        return state.cancelCount
      },
    }
  })

  await page.goto('/')
})

Given('validation response for {string} is valid with title {string}', async ({ page }, url: string, title: string) => {
  await readMock(page, 'window.__bddMock.setValidateResponse(args[0], args[1])', url, {
    valid: true,
    title,
    isAudioOnly: false,
  })
})

Given('validation response for {string} is invalid with error {string}', async ({ page }, url: string, error: string) => {
  await readMock(page, 'window.__bddMock.setValidateResponse(args[0], args[1])', url, {
    valid: false,
    error,
  })
})

Given('browse folder returns {string}', async ({ page }, folder: string) => {
  await readMock(page, 'window.__bddMock.setBrowseFolderResult(args[0])', {
    success: true,
    path: folder,
  })
})

Given('start download succeeds', async ({ page }) => {
  await readMock(page, 'window.__bddMock.setStartDownloadResult(args[0])', { success: true })
})

When('I enter URL {string}', async ({ page }, url: string) => {
  await urlInput(page).fill(url)
  await page.waitForTimeout(700)
})

When('I select audio format', async ({ page }) => {
  await page.getByRole('button', { name: 'Audio · MP3' }).click()
})

When('I select video format', async ({ page }) => {
  await page.getByRole('button', { name: 'Video', exact: true }).click()
})

When('I select quality {string}', async ({ page }, quality: string) => {
  await qualitySelect(page).selectOption(quality)
})

When('I enable transcript download', async ({ page }) => {
  await page.getByLabel('Download transcript').check()
})

When('I set destination to {string}', async ({ page }, destination: string) => {
  await destinationInput(page).fill(destination)
  await destinationInput(page).blur()
})

When('I click Browse for destination', async ({ page }) => {
  await page.getByRole('button', { name: 'Browse' }).click()
})

When('I start the download', async ({ page }) => {
  await downloadButton(page).click()
})

When('download reports status {string} progress {float} message {string}', async ({ page }, status: string, progress: number, message: string) => {
  await readMock(page, 'window.__bddMock.emitProgress(args[0])', { status, progress, message })
})

When('download completes successfully with file {string}', async ({ page }, file: string) => {
  await readMock(page, 'window.__bddMock.emitComplete(args[0])', {
    success: true,
    message: 'Download complete!',
    filename: file,
  })
})

When('transcript text arrives {string}', async ({ page }, text: string) => {
  await readMock(page, 'window.__bddMock.emitTranscript(args[0])', { text })
})

When('I click transcript toggle', async ({ page }) => {
  await page.getByRole('button', { name: /Show|Hide/ }).click()
})

When('I click Show in folder', async ({ page }) => {
  await page.getByRole('button', { name: 'Show in folder' }).click()
})

When('I cancel the download', async ({ page }) => {
  await page.getByRole('button', { name: /Cancel/i }).click()
})

Then('the title bar shows the app name and version', async ({ page }) => {
  await expect(page.locator('.titlebar-title')).toContainText('Media Downloader v')
})

Then('the download button is disabled until a URL is entered', async ({ page }) => {
  await expect(downloadButton(page)).toBeDisabled()
})

Then('the download button is enabled', async ({ page }) => {
  await expect(downloadButton(page)).toBeEnabled()
})

Then('URL status contains {string}', async ({ page }, text: string) => {
  await expect(page.locator('.url-status')).toContainText(text)
})

Then('the quality options are {string}', async ({ page }, csv: string) => {
  const expected = csv.split(',').map((s: string) => s.trim())
  const actual = (await qualitySelect(page).locator('option').allTextContents()).map((s: string) => s.trim())
  expect(actual).toEqual(expected)
})

Then('destination is {string}', async ({ page }, expectedDestination: string) => {
  await expect(destinationInput(page)).toHaveValue(expectedDestination)
})

Then('last start request {word} is {string}', async ({ page }, key: string, expected: string) => {
  const actual = await readMock(page, 'window.__bddMock.getLastStartRequest()?.[args[0]]', key)
  expect(actual).toBe(expected)
})

Then('last start request {word} is true', async ({ page }, key: string) => {
  const actual = await readMock(page, 'window.__bddMock.getLastStartRequest()?.[args[0]]', key)
  expect(actual).toBe(true)
})

Then('progress message contains {string}', async ({ page }, text: string) => {
  await expect(page.locator('.progress-msg')).toContainText(text)
})

Then('Show in folder action is available', async ({ page }) => {
  await expect(page.getByRole('button', { name: 'Show in folder' })).toBeVisible()
})

Then('shell show item is called with {string}', async ({ page }, file: string) => {
  const calls = await readMock(page, 'window.__bddMock.getShowItemCalls()')
  expect(calls).toContain(file)
})

Then('transcript section is visible', async ({ page }) => {
  await expect(page.locator('.section-label').filter({ hasText: 'Transcript' })).toBeVisible()
})

Then('transcript text contains {string}', async ({ page }, text: string) => {
  await expect(page.locator('.transcript-box')).toContainText(text)
})

Then('cancel button is shown', async ({ page }) => {
  await expect(page.getByRole('button', { name: /Cancel/i })).toBeVisible()
})

Then('cancel download was requested {int} time', async ({ page }, times: number) => {
  const count = await readMock(page, 'window.__bddMock.getCancelCount()')
  expect(count).toBe(times)
})
