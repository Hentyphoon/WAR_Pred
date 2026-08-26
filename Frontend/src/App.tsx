import { Routes, Route } from 'react-router-dom'
import Search from './Search'
import Player from './Player'
import ErrorPage from './ErrorPage'
import Predictions from './predictions'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Search />} />
      <Route path="/player/:id" element={<Player />} />
      <Route path="/ErrorPage" element={<ErrorPage />} />
      <Route path="/predictions/:id" element={<Predictions />} />
    </Routes>
  )
}

export default App  