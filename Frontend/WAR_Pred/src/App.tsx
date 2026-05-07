import { Routes, Route } from 'react-router-dom'
import Search from './Search'
import Player from './Player'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Search />} />
      <Route path="/player/:name" element={<Player />} />
    </Routes>
  )
}

export default App  