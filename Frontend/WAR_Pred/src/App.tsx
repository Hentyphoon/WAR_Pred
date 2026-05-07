import { useState } from 'react'
import './App.css'
import { useNavigate } from 'react-router-dom'

function App() {
  const [search, setSearch] = useState('')
  const nav = useNavigate()

  const handleSearch = () => {
    
  }

  return (
    <div className="App">
      <h1 className="title">Please enter player name</h1>
      <input
        className="search-input"
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
    </div>
  )
}

export default App
