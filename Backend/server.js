const express = require('express')
const cors = require('cors')
require('dotenv').config()

const pool = require('./db/pool')

const app = express()

app.use(cors())
app.use(express.json())

app.get('/players/:id', async (req, res) => {
  const id = req.params.id

  try {
    const result = await pool.query(
      `
      SELECT *
      FROM "playerstat"
      WHERE "idfg" = $1
      ORDER BY "season" ASC
      `,
      [id]
    )

    res.json(result.rows)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Player fetch failed' })
  }
})


app.get('/search', async (req, res) => {
  const query = req.query.q?.trim()

  if (!query) return res.json([])

  try {
    const result = await pool.query(
      `
      SELECT
        "idfg",
        "name",
        MIN("season") AS start_season,
        MAX("season") AS end_season
      FROM "playerstat"
      WHERE "name" ILIKE $1
      GROUP BY "idfg", "name"
      ORDER BY "name"
      LIMIT 10
      `,
      [`%${query}%`]
    )

    res.json(result.rows)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Search failed' })
  }
})

const PORT = process.env.PORT || 8000

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})