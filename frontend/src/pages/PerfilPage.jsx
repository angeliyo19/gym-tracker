import { useState } from 'react'
import { actualizarMiPerfil } from '../api/usuarios'
import { useAuth } from '../context/AuthContext'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { PageHeader } from '../components/ui/PageHeader'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

// Los <select> nativos traen su propia flecha con la apariencia por defecto
// del navegador, que no se puede recolorear ni alinear con el resto de la
// UI. Se oculta con appearance-none y se sustituye por un icono propio,
// igual que ya se hace con otros iconos de la app (ver ThemeToggle).
const CAMPO_SELECT =
  'appearance-none rounded-lg border border-border bg-surface py-2 pl-3 pr-9 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

function IconoFlecha(props) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="m6 9 6 6 6-6" />
    </svg>
  )
}

function SelectEstilizado({ value, onChange, children }) {
  return (
    <div className="relative">
      <select value={value} onChange={onChange} className={`block w-full ${CAMPO_SELECT}`}>
        {children}
      </select>
      <IconoFlecha className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
    </div>
  )
}

export function PerfilPage() {
  const { usuario, actualizarUsuario } = useAuth()

  const [valores, setValores] = useState({
    nombre: usuario.nombre,
    edad: usuario.edad,
    peso: usuario.peso,
    altura: usuario.altura,
    sexo: usuario.sexo,
    objetivo: usuario.objetivo,
  })
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState(null)
  const [guardado, setGuardado] = useState(false)

  function actualizarCampo(campo, valor) {
    setValores((actuales) => ({ ...actuales, [campo]: valor }))
    setGuardado(false)
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError(null)
    setGuardando(true)
    try {
      const actualizado = await actualizarMiPerfil({
        ...valores,
        edad: Number(valores.edad),
        peso: Number(valores.peso),
        altura: Number(valores.altura),
      })
      actualizarUsuario(actualizado)
      setGuardado(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <main className="mx-auto max-w-sm px-8 py-10">
      <PageHeader title="Mi perfil" description="Tus datos personales." />

      <Card className="mt-6 p-5">
        <form onSubmit={manejarSubmit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Email</label>
            <input
              type="email"
              value={usuario.email}
              disabled
              className={`block w-full ${CAMPO} cursor-not-allowed opacity-60`}
            />
            <p className="mt-1 text-xs text-ink-muted">El email no se puede cambiar por ahora.</p>
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Nombre</label>
            <input
              required
              value={valores.nombre}
              onChange={(e) => actualizarCampo('nombre', e.target.value)}
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
              <SelectEstilizado
                value={valores.sexo}
                onChange={(e) => actualizarCampo('sexo', e.target.value)}
              >
                <option value="masculino">Masculino</option>
                <option value="femenino">Femenino</option>
              </SelectEstilizado>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-ink-muted">Objetivo</label>
              <SelectEstilizado
                value={valores.objetivo}
                onChange={(e) => actualizarCampo('objetivo', e.target.value)}
              >
                <option value="volumen">Volumen</option>
                <option value="definicion">Definición</option>
                <option value="mantenimiento">Mantenimiento</option>
              </SelectEstilizado>
            </div>
          </div>

          {error && (
            <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
          )}
          {guardado && !error && (
            <p className="rounded-lg bg-accent/10 p-3 text-sm text-accent">Cambios guardados.</p>
          )}

          <Button type="submit" variant="primary" disabled={guardando} className="w-full">
            {guardando ? 'Guardando...' : 'Guardar cambios'}
          </Button>
        </form>
      </Card>
    </main>
  )
}
