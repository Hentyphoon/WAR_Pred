import { useState } from 'react'
import './Search.css'
import { useNavigate } from 'react-router-dom'


function Search() {
  const [search, setSearch] = useState('')
  const nav = useNavigate()

  const handleSearch = async () => {
    if (search.trim() === '') {
      nav('/ErrorPage/')
      return
    }

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/search?q=${encodeURIComponent(search.trim())}`)
      const data = await res.json()

      if (data.length === 0) {
        nav('/ErrorPage/')
        return
      }
      const player = data[0]//replace with better search later

      nav(`/Player/${player.idfg}`)
    } catch (err) {
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
      onChange={(e) => setSearch(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') {
          handleSearch()
        }
      }}
    />
  </div>
)
}

export default Search