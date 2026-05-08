import { Routes, Route } from 'react-router-dom'
import Search from './Search'
import Player from './Player'
import ErrorPage from './ErrorPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Search />} />
      <Route path="/player/:name" element={<Player />} />
      <Route path="/ErrorPage" element={<ErrorPage />} />
    </Routes>
  )
}

export default App  