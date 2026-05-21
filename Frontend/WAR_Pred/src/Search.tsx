import { useState } from 'react'
import './Search.css'
import { useNavigate } from 'react-router-dom'


function Search() {
  const [search, setSearch] = useState('')
  const nav = useNavigate()

  const handleSearch = async () => {
    console.log(`Searching for: ${search}`)
    if (search.trim() === '') {
      nav('/ErrorPage/')
      console.log('Empty search query')
      return
    }

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/search?q=${encodeURIComponent(search.trim())}`)
      const data = await res.json()

      if (data.length === 0) {
        nav('/ErrorPage/')
        console.log('No player found')
        return
      }
      const player = data[0]

      nav(`/Player/${player.idfg}`)
    } catch (err) {
      console.error(err)
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
    <button onClick={handleSearch}>Search</button>  {/* add this */}
  </div>
)
}

export default Search