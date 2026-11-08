import { useState } from 'react'
import './Search.css'
import { useNavigate } from 'react-router-dom'


type SearchResult = {
  idfg: string
  name: string
  start_season: number
  end_season: number
}

function Search() {
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const nav = useNavigate()

  const handleSearch = async () => {
    if (search.trim() === '') {
      nav('/ErrorPage/')
      return
    }

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/search?q=${encodeURIComponent(search.trim())}`)
      const data: SearchResult[] = await res.json()

      if (data.length === 0) {
        nav('/ErrorPage/')
        return
      }
      if (data.length === 1) {
        nav(`/player/${data[0].idfg}`)
        return
      }

      setResults(data)
    } catch {
      nav('/ErrorPage/')
    }
  }

return (
  <div className="Search">
    <h1 className="title">Please enter player name</h1>
    <input
      className="search-input"
      type="text"
      value={search}
      onChange={(e) => {
        setSearch(e.target.value)
        setResults([])
      }}
      onKeyDown={(e) => {
        if (e.key === 'Enter') {
          handleSearch()
        }
      }}
    />
    {results.length > 0 && (
      <ul className="search-results">
        {results.map((player) => (
          <li key={player.idfg}>
            <button onClick={() => nav(`/player/${player.idfg}`)}>
              {player.name} ({player.start_season}–{player.end_season})
            </button>
          </li>
        ))}
      </ul>
    )}
  </div>
)
}

export default Search