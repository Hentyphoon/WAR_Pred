import { useNavigate } from 'react-router-dom'
import './ErrorPage.css'

function ErrorPage() {
  const nav = useNavigate()

  return (
    <div className="Error">
      <h1 className="error-title">Error: Invalid player name</h1>
      <button className="error-btn" onClick={() => nav('//')}>
        Click to go back
      </button>
    </div>
  )
}

export default ErrorPage