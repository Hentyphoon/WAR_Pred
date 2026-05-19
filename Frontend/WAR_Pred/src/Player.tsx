import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'

function Player() {
  const { id } = useParams()
  type PlayerSeason = {
  idfg: string
  name: string
  season: number
  age: number
  pa: number
  ab: number
  h: number
  "1B": number
  "2B": number
  "3B": number
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
  const [player, setPlayer] = useState<PlayerSeason[]>([])
  useEffect(() => {
    const fetchPlayer = async () => {
      const res = await fetch(`http://localhost:8000/players/${id}`)
      const data = await res.json()
      setPlayer(data)
    }

    fetchPlayer()
  }, [id])
  console.log(player)
  return (
    <div className="Player">
      <h1>{id}</h1>

      {player.map((season, i) => (
        <div key={i}>
          <p>{season.season}</p>
          <p>HR: {season.hr}</p>
          <p>AVG stats etc...</p>
        </div>
      ))}
    </div>
  )
}

export default Player