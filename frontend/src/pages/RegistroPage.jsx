import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from '../components/ui/Button'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

const VALORES_INICIALES = {
  nombre: '',
  email: '',
  edad: '',
  peso: '',
  altura: '',
  sexo: 'masculino',
  objetivo: 'volumen',
  password: '',
}

export function RegistroPage() {
  const { registro } = useAuth()
  const navigate = useNavigate()
  const [valores, setValores] = useState(VALORES_INICIALES)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  function actualizarCampo(campo, valor) {
    setValores((actuales) => ({ ...actuales, [campo]: valor }))
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await registro({
        ...valores,
        edad: Number(valores.edad),
        peso: Number(valores.peso),
        altura: Number(valores.altura),
      })
      navigate('/rutinas', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="mx-auto max-w-sm px-8 py-16">
      <h1 className="font-heading text-2xl font-semibold text-ink">Crea tu cuenta</h1>

      <form onSubmit={manejarSubmit} className="mt-6 space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink-muted">Nombre</label>
          <input
            required
            value={valores.nombre}
            onChange={(e) => actualizarCampo('nombre', e.target.value)}
            className={`block w-full ${CAMPO}`}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink-muted">Email</label>
          <input
            type="email"
            required
            value={valores.email}
            onChange={(e) => actualizarCampo('email', e.target.value)}
            className={`block w-full ${CAMPO}`}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink-muted">Contraseña</label>
          <input
            type="password"
            required
            value={valores.password}
            onChange={(e) => actualizarCampo('password', e.target.value)}
            className={`block w-full ${CAMPO}`}
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Edad</label>
            <input
              type="number"
              min={1}
              required
              value={valores.edad}
              onChange={(e) => actualizarCampo('edad', e.target.value)}
              className={`block w-full ${CAMPO}`}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Peso (kg)</label>
            <input
              type="number"
              step="0.1"
              required
              value={valores.peso}
              onChange={(e) => actualizarCampo('peso', e.target.value)}
              className={`block w-full ${CAMPO}`}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Altura (m)</label>
            <input
              type="number"
              step="0.01"
              required
              value={valores.altura}
              onChange={(e) => actualizarCampo('altura', e.target.value)}
              className={`block w-full ${CAMPO}`}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Sexo</label>
            <select
              value={valores.sexo}
              onChange={(e) => actualizarCampo('sexo', e.target.value)}
              className={`block w-full ${CAMPO}`}
            >
              <option value="masculino">Masculino</option>
              <option value="femenino">Femenino</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Objetivo</label>
            <select
              value={valores.objetivo}
              onChange={(e) => actualizarCampo('objetivo', e.target.value)}
              className={`block w-full ${CAMPO}`}
            >
              <option value="volumen">Volumen</option>
              <option value="definicion">Definición</option>
              <option value="mantenimiento">Mantenimiento</option>
            </select>
          </div>
        </div>

        {error && (
          <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
        )}

        <Button type="submit" variant="primary" disabled={enviando} className="w-full">
          {enviando ? 'Creando cuenta...' : 'Crear cuenta'}
        </Button>
      </form>

      <p className="mt-4 text-sm text-ink-muted">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="font-medium text-accent hover:text-accent-hover">
          Inicia sesión
        </Link>
      </p>
    </main>
  )
}
