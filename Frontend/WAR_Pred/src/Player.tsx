import { useParams } from 'react-router-dom'

function Player() {
  const { name } = useParams()

  return (
    <div className="Player">
      <h1>{name}</h1>
      {/* fetch and display player stats here */}
    </div>
  )
}

export default Player