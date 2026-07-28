import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from '../components/ui/Button'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await login(email, password)
      navigate('/rutinas', { replace: true })
    } catch {
      setError('Email o contraseña incorrectos')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="mx-auto max-w-sm px-8 py-16">
      <h1 className="font-heading text-2xl font-semibold text-ink">Inicia sesión</h1>

      <form onSubmit={manejarSubmit} className="mt-6 space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink-muted">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={`block w-full ${CAMPO}`}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink-muted">Contraseña</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`block w-full ${CAMPO}`}
          />
        </div>

        {error && (
          <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
        )}

        <Button type="submit" variant="primary" disabled={enviando} className="w-full">
          {enviando ? 'Entrando...' : 'Entrar'}
        </Button>
      </form>

      <p className="mt-4 text-sm text-ink-muted">
        ¿No tienes cuenta?{' '}
        <Link to="/registro" className="font-medium text-accent hover:text-accent-hover">
          Regístrate
        </Link>
      </p>
    </main>
  )
}
