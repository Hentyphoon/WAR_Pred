import { useParams, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import './Player.css'

type PlayerSeason = {
  idfg: string
  name: string
  season: number
  age: number
  pa: number
  ab: number
  h: number
  '1B': number
  '2B': number
  '3B': number
  hr: number
  bb: number
  ibb: number
  ubb: number
  hbp: number
  sb: number
  cs: number
  gdp: number
  gdp_opp: number
  sf: number
  woba: number
}

function Player() {
  const { id } = useParams()
  const nav = useNavigate()
  const [player, setPlayer] = useState<PlayerSeason[]>([])

  useEffect(() => {
    const fetchPlayer = async () => {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/players/${id}`)
      const data = await res.json()
      setPlayer(data)
    }

    fetchPlayer()
  }, [id])

  const name = player[0]?.name ?? id

  return (
  <div className="Player">
    <div className="player-top">
      <button className="back-btn" onClick={() => nav('/')}>
        Home
      </button>

      <button
        className="predict-btn"
        onClick={() => nav(`/predictions/${id}`)}
      >
        View Predictions
      </button>
    </div>

    <div className="player-header">
      <h1>{name}</h1>
    </div>

    <div className="stitch" />

    <div className="season-list">
      {player.map((season, i) => (
        <div className="season-row" key={i}>
          <span className="season-year">{season.season}</span>

          <div className="stat">
            <span className="stat-label">AVG</span>
            <span className="stat-value">
              {(season.h / season.ab).toFixed(3).replace(/^0/, '')}
            </span>
          </div>

          <div className="stat">
            <span className="stat-label">HR</span>
            <span className="stat-value">{season.hr}</span>
          </div>

          <div className="stat">
            <span className="stat-label">wOBA</span>
            <span className="stat-value">{season.woba.toFixed(3)}</span>
          </div>
        </div>
      ))}
    </div>
  </div>
)
}

export default Player