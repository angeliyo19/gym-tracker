import { useEffect, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { finalizarSesion, getSesion } from '../api/sesiones'
import { EjercicioEnVivo } from '../components/EjercicioEnVivo'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/ui/EmptyState'
import { PageHeader } from '../components/ui/PageHeader'

export function SesionEnVivoPage() {
  const { id: sesionId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [error, setError] = useState(null)
  const [finalizando, setFinalizando] = useState(false)

  // location.state es solo una optimización para evitar el parpadeo de carga
  // al venir de "Iniciar sesión" en RutinaDetalle: se usa como valor inicial
  // optimista, pero SIEMPRE se vuelve a pedir al backend en el montaje. Un F5
  // no limpia location.state (el navegador conserva window.history.state al
  // recargar el mismo documento), así que si aquí nos fiáramos únicamente de
  // "ya tengo location.state, no hace falta pedir nada", una recarga después
  // de guardar una serie seguiría mostrando para siempre la foto vieja
  // capturada en la navegación original (sin la serie recién guardada).
  const [sesion, setSesion] = useState(location.state?.sesion ?? null)
  const [cargando, setCargando] = useState(!location.state?.sesion)

  useEffect(() => {
    getSesion(sesionId)
      .then(setSesion)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }, [sesionId])

  const rutina = sesion?.rutina ?? null
  const soloLectura = sesion?.completada ?? false
  const ultimasSeries = sesion?.ultimas_series ?? []
  const referenciasPorEjercicio = Object.fromEntries(
    ultimasSeries.map((referencia) => [referencia.ejercicio_id, referencia]),
  )
  const seriesRegistradas = sesion?.series_registradas ?? []
  const seriesGuardadasPorEjercicio = Object.fromEntries(
    seriesRegistradas.map((grupo) => [grupo.ejercicio_id, grupo.series]),
  )

  async function manejarFinalizar() {
    setError(null)
    setFinalizando(true)
    try {
      await finalizarSesion(sesionId)
      navigate('/entrenamiento/rutinas')
    } catch (err) {
      setError(err.message)
      setFinalizando(false)
    }
  }

  if (cargando) {
    return (
      <main className="mx-auto max-w-xl px-8 py-10">
        <p className="text-ink-muted">Cargando sesión...</p>
      </main>
    )
  }

  if (!rutina) {
    return (
      <main className="mx-auto max-w-xl px-8 py-10">
        <EmptyState
          title="No se encontró la información de la sesión"
          description="Puede que la sesión no exista o no te pertenezca. Vuelve a Rutinas e inícialas de nuevo desde ahí."
          action={
            <Button variant="primary" onClick={() => navigate('/entrenamiento/rutinas')}>
              Volver a rutinas
            </Button>
          }
        />
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      <PageHeader
        title={rutina.nombre}
        description={
          soloLectura
            ? 'Sesión completada. Estás viendo un registro histórico.'
            : 'Registra tus series a medida que las completas.'
        }
        action={
          soloLectura ? (
            <span className="whitespace-nowrap rounded-full bg-accent/10 px-3 py-1.5 text-sm font-medium text-accent">
              ✓ Completada
            </span>
          ) : (
            <Button variant="primary" onClick={manejarFinalizar} disabled={finalizando}>
              {finalizando ? 'Finalizando...' : 'Finalizar sesión'}
            </Button>
          )
        }
      />

      {error && (
        <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      {rutina.ejercicios.length === 0 && (
        <div className="mt-6">
          <EmptyState
            title="Esta rutina no tiene ejercicios"
            description={
              soloLectura
                ? 'No había nada que registrar en esta sesión.'
                : 'No hay nada que registrar. Puedes finalizar la sesión directamente.'
            }
          />
        </div>
      )}

      <div className="mt-6 space-y-4">
        {[...rutina.ejercicios]
          .sort((a, b) => a.orden - b.orden)
          .map((item) => (
            <EjercicioEnVivo
              key={`${item.ejercicio.id}-${item.orden}`}
              sesionId={sesionId}
              ejercicio={item.ejercicio}
              seriesObjetivo={item.series_objetivo}
              repeticionesObjetivo={item.repeticiones_objetivo}
              referencia={referenciasPorEjercicio[item.ejercicio.id]}
              seriesGuardadas={seriesGuardadasPorEjercicio[item.ejercicio.id] ?? []}
              soloLectura={soloLectura}
            />
          ))}
      </div>
    </main>
  )
}
