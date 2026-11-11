// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, screen, within } from '@testing-library/react'
import Player from './Player'
import { mockFetch, renderPage } from './test-utils'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

const season = (overrides: object) => ({
  idfg: 'aardsda01', name: 'David Aardsma', season: 2006, age: 25, pa: 3, ab: 2, h: 1,
  '1B': 1, '2B': 0, '3B': 0, hr: 0, bb: 1, ibb: 0, ubb: 1, hbp: 0, sb: 0, cs: 0,
  gdp: 0, gdp_opp: 0, sf: 0, woba: 0.567, ...overrides,
})

it('shows a dash instead of crashing when a season has no wOBA or at-bats', async () => {
  mockFetch([{ body: [season({ season: 2004, ab: 0, h: 0, woba: null }), season({})] }])
  renderPage('/player/aardsda01', '/player/:id', <Player />)

  const row2004 = (await screen.findByText('2004')).closest('.season-row') as HTMLElement
  expect(within(row2004).getAllByText('—')).toHaveLength(2)

  const row2006 = screen.getByText('2006').closest('.season-row') as HTMLElement
  expect(within(row2006).getByText('.500')).toBeTruthy()
  expect(within(row2006).getByText('0.567')).toBeTruthy()
})

it('shows the player name and links to predictions', async () => {
  mockFetch([{ body: [season({})] }])
  renderPage('/player/aardsda01', '/player/:id', <Player />)

  expect(await screen.findByRole('heading', { name: 'David Aardsma' })).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'View Predictions' }))
  expect(screen.getByTestId('path').textContent).toBe('/predictions/aardsda01')
})
