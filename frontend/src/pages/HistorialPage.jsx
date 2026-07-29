import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getRutinas } from '../api/rutinas'
import { getSesiones } from '../api/sesiones'
import { EntrenamientoTabs } from '../components/EntrenamientoTabs'
import { Card } from '../components/ui/Card'
import { EmptyState } from '../components/ui/EmptyState'
import { PageHeader } from '../components/ui/PageHeader'
import { formatearFecha } from '../utils/fecha'

export function HistorialPage() {
  const navigate = useNavigate()
  const [sesiones, setSesiones] = useState([])
  const [rutinasPorId, setRutinasPorId] = useState({})
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    setCargando(true)
    Promise.all([getSesiones(), getRutinas()])
      .then(([sesionesRecibidas, rutinas]) => {
        setSesiones(sesionesRecibidas)
        setRutinasPorId(Object.fromEntries(rutinas.map((rutina) => [rutina.id, rutina])))
      })
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }, [])

  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      <EntrenamientoTabs />

      <PageHeader title="Historial" description="Tus sesiones de entrenamiento pasadas." />

      {cargando && <p className="mt-6 text-ink-muted">Cargando...</p>}

      {error && (
        <p className="mt-6 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      {!cargando && !error && sesiones.length === 0 && (
        <div className="mt-6">
          <EmptyState
            title="Todavía no hay sesiones registradas"
            description="Inicia una rutina desde la pestaña Rutinas para empezar a entrenar."
          />
        </div>
      )}

      {!cargando && !error && sesiones.length > 0 && (
        <Card className="mt-6 divide-y divide-border overflow-hidden">
          {sesiones.map((sesion) => (
            <button
              key={sesion.id}
              type="button"
              onClick={() => navigate(`/entrenamiento/sesiones/${sesion.id}`)}
              className="flex w-full items-center justify-between px-4 py-3.5 text-left transition-colors hover:bg-surface-hover"
            >
              <div>
                <span className="font-medium text-ink">
                  {rutinasPorId[sesion.rutina_id]?.nombre ?? 'Rutina eliminada'}
                </span>
                <p className="text-xs text-ink-muted">{formatearFecha(sesion.fecha)}</p>
              </div>
              <span
                className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ${
                  sesion.completada
                    ? 'bg-accent/10 text-accent'
                    : 'border border-border text-ink-muted'
                }`}
              >
                {sesion.completada ? '✓ Completada' : 'En progreso'}
              </span>
            </button>
          ))}
        </Card>
      )}
    </main>
  )
}
