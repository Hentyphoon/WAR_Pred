// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, screen } from '@testing-library/react'
import Predictions from './predictions'
import { formatStat } from './formatStat'
import { mockFetch, renderPage } from './test-utils'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

it('shows the predicted components', async () => {
  mockFetch([{ body: { idfg: 'troutmi01', season: 2025, prediction: { bsr: 0.0, wraa: 15.74, rlr: 9.56, owar: 2.61 } } }])
  renderPage('/predictions/troutmi01', '/predictions/:id', <Predictions />)

  expect(await screen.findByText('15.74')).toBeTruthy()
  expect(screen.getByText('9.56')).toBeTruthy()
  expect(screen.getByText('0.00')).toBeTruthy()
})

it('marks tiny non-zero values instead of rounding them to 0.00', async () => {
  mockFetch([{ body: { idfg: 'troutmi01', season: 2025, prediction: { bsr: 0.0044, wraa: -0.0001, rlr: 9.56, owar: 2.61 } } }])
  renderPage('/predictions/troutmi01', '/predictions/:id', <Predictions />)

  expect(await screen.findByText('<0.01')).toBeTruthy()
  expect(screen.getByText('>-0.01')).toBeTruthy()
})

it('formats values to two decimals', () => {
  expect(formatStat(0)).toBe('0.00')
  expect(formatStat(0.005)).toBe('0.01')
  expect(formatStat(-0.0049)).toBe('>-0.01')
  expect(formatStat(-1.234)).toBe('-1.23')
})

it('explains why there is no prediction', async () => {
  const detail = 'No prediction available. Predictions only cover hitters active in 2024 with at least 100 PA over the last three seasons.'
  mockFetch([{ status: 404, body: { detail } }])
  renderPage('/predictions/ruthba01', '/predictions/:id', <Predictions />)

  expect((await screen.findByRole('alert')).textContent).toBe(detail)
})

it('goes back to the player page', async () => {
  mockFetch([{ status: 404, body: { detail: 'none' } }])
  renderPage('/predictions/ruthba01', '/predictions/:id', <Predictions />)

  await screen.findByRole('alert')
  fireEvent.click(screen.getByRole('button', { name: 'Back' }))

  expect(screen.getByTestId('path').textContent).toBe('/player/ruthba01')
})
