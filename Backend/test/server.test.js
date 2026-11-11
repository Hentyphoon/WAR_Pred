const { test, before, after, beforeEach } = require('node:test')
const assert = require('node:assert/strict')

// Swap in a fake pool before server.js loads, so no database is needed.
const pool = { calls: [], result: { rows: [] }, error: null }
pool.query = async (sql, params) => {
  pool.calls.push({ sql, params })
  if (pool.error) throw pool.error
  return pool.result
}
const poolPath = require.resolve('../db/pool')
require.cache[poolPath] = { id: poolPath, filename: poolPath, loaded: true, exports: pool }

const app = require('../server')

let server
let baseUrl

before(async () => {
  server = app.listen(0)
  await new Promise((resolve) => server.once('listening', resolve))
  baseUrl = `http://127.0.0.1:${server.address().port}`
})

after(() => server.close())

beforeEach(() => {
  pool.calls = []
  pool.result = { rows: [] }
  pool.error = null
})

test('GET /players/:id returns the player seasons', async () => {
  pool.result = { rows: [{ idfg: 'ruthba01', season: 1921, pa: 693 }] }

  const res = await fetch(`${baseUrl}/players/ruthba01`)

  assert.equal(res.status, 200)
  assert.deepEqual(await res.json(), [{ idfg: 'ruthba01', season: 1921, pa: 693 }])
  assert.deepEqual(pool.calls[0].params, ['ruthba01'])
})

test('GET /players/:id passes the id as a parameter, not in the SQL', async () => {
  await fetch(`${baseUrl}/players/${encodeURIComponent("x' OR '1'='1")}`)

  assert.deepEqual(pool.calls[0].params, ["x' OR '1'='1"])
  assert.ok(!pool.calls[0].sql.includes("OR '1'='1"))
})

test('GET /players/:id returns 500 when the database fails', async (t) => {
  t.mock.method(console, 'error', () => {})
  pool.error = new Error('connection lost')

  const res = await fetch(`${baseUrl}/players/ruthba01`)

  assert.equal(res.status, 500)
  assert.deepEqual(await res.json(), { error: 'Player fetch failed' })
})

test('GET /search matches names containing the query', async () => {
  pool.result = { rows: [{ idfg: 'griffke01', name: 'Ken Griffey' }] }

  const res = await fetch(`${baseUrl}/search?q=${encodeURIComponent('  Griffey ')}`)

  assert.equal(res.status, 200)
  assert.deepEqual(await res.json(), [{ idfg: 'griffke01', name: 'Ken Griffey' }])
  assert.deepEqual(pool.calls[0].params, ['%Griffey%'])
})

test('GET /search skips the database for an empty query', async () => {
  for (const q of ['', '   ']) {
    const res = await fetch(`${baseUrl}/search?q=${encodeURIComponent(q)}`)
    assert.deepEqual(await res.json(), [])
  }
  assert.equal(pool.calls.length, 0)
})

test('GET /search returns 500 when the database fails', async (t) => {
  t.mock.method(console, 'error', () => {})
  pool.error = new Error('connection lost')

  const res = await fetch(`${baseUrl}/search?q=Ruth`)

  assert.equal(res.status, 500)
  assert.deepEqual(await res.json(), { error: 'Search failed' })
})
