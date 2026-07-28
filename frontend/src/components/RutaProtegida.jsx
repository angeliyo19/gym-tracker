import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function RutaProtegida({ children }) {
  const { usuario, cargando } = useAuth()

  if (cargando) {
    return <p className="mx-auto max-w-xl px-8 py-10 text-ink-muted">Cargando...</p>
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  return children
}
