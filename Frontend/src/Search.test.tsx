// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, screen } from '@testing-library/react'
import Search from './Search'
import { mockFetch, renderPage } from './test-utils'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function search(text: string) {
  const input = screen.getByRole('textbox')
  fireEvent.change(input, { target: { value: text } })
  fireEvent.keyDown(input, { key: 'Enter' })
}

const griffeys = [
  { idfg: 'griffke01', name: 'Ken Griffey', start_season: 1973, end_season: 1991 },
  { idfg: 'griffke02', name: 'Ken Griffey', start_season: 1989, end_season: 2010 },
]

it('lists players when the name matches more than one', async () => {
  mockFetch([{ body: griffeys }])
  renderPage('/', '/', <Search />)

  search('Ken Griffey')
  fireEvent.click(await screen.findByRole('button', { name: 'Ken Griffey (1989–2010)' }))

  expect(screen.getByTestId('path').textContent).toBe('/player/griffke02')
})

it('goes straight to the player when there is one match', async () => {
  mockFetch([{ body: [griffeys[0]] }])
  renderPage('/', '/', <Search />)

  search('Griffey')

  expect((await screen.findByTestId('path')).textContent).toBe('/player/griffke01')
})

it('shows the error page when nothing matches', async () => {
  mockFetch([{ body: [] }])
  renderPage('/', '/', <Search />)

  search('Nobody')

  expect((await screen.findByTestId('path')).textContent).toBe('/ErrorPage/')
})

it('does not call the API for a blank search', () => {
  const fetchMock = mockFetch([])
  renderPage('/', '/', <Search />)

  search('   ')

  expect(fetchMock).not.toHaveBeenCalled()
  expect(screen.getByTestId('path').textContent).toBe('/ErrorPage/')
})

it('clears old results when the search changes', async () => {
  mockFetch([{ body: griffeys }])
  renderPage('/', '/', <Search />)

  search('Ken Griffey')
  await screen.findAllByRole('listitem')
  fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Ken' } })

  expect(screen.queryAllByRole('listitem')).toHaveLength(0)
})
