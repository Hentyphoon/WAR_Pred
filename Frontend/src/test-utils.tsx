import { vi } from 'vitest'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'

export function mockFetch(responses: Array<{ status?: number; body: unknown }>) {
  const fetchMock = vi.fn()
  for (const { status = 200, body } of responses) {
    fetchMock.mockResolvedValueOnce({
      ok: status >= 200 && status < 300,
      status,
      json: async () => body,
    })
  }
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

function CurrentPath() {
  return <p data-testid="path">{useLocation().pathname}</p>
}

// Renders one page at a URL; any navigation away shows the new path instead.
export function renderPage(path: string, routePath: string, page: ReactElement) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path={routePath} element={page} />
        <Route path="*" element={<CurrentPath />} />
      </Routes>
    </MemoryRouter>,
  )
}
