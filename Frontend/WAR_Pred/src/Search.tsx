import { useState } from 'react'
import './Search.css'
import { useNavigate } from 'react-router-dom'


function Search() {
  const [search, setSearch] = useState('')
  const nav = useNavigate()

  const handleSearch = () => {
    if (search.trim() !== '') { // change to validate player name here
      //nav(`/player/${search.trim()}`)
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
          }}}
      />
    </div>
  )
}

export default Search
