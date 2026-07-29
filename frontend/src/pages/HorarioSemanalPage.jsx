import { useEffect, useState } from 'react'
import { getRutinas } from '../api/rutinas'
import {
  actualizarRutinaProgramada,
  crearRutinaProgramada,
  eliminarRutinaProgramada,
  getRutinasProgramadas,
} from '../api/rutinasProgramadas'
import { EntrenamientoTabs } from '../components/EntrenamientoTabs'
import { Card } from '../components/ui/Card'
import { EmptyState } from '../components/ui/EmptyState'
import { PageHeader } from '../components/ui/PageHeader'
import { DIA_SEMANA_ETIQUETA, DIAS_SEMANA } from '../utils/dias'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent disabled:opacity-60'

export function HorarioSemanalPage() {
  const [rutinas, setRutinas] = useState([])
  const [programadaPorDia, setProgramadaPorDia] = useState({})
  const [guardandoDia, setGuardandoDia] = useState(null)
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    Promise.all([getRutinas(), getRutinasProgramadas()])
      .then(([rutinasData, programadasData]) => {
        setRutinas(rutinasData)
        setProgramadaPorDia(
          Object.fromEntries(programadasData.map((programada) => [programada.dia_semana, programada])),
        )
      })
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }, [])

  async function manejarCambio(dia, valor) {
    setError(null)
    setGuardandoDia(dia)
    const existente = programadaPorDia[dia]
    try {
      if (!valor) {
        if (existente) {
          await eliminarRutinaProgramada(existente.id)
          setProgramadaPorDia((actuales) => {
            const { [dia]: _quitado, ...resto } = actuales
            return resto
          })
        }
      } else if (existente) {
        const actualizada = await actualizarRutinaProgramada(existente.id, {
          rutina_id: Number(valor),
        })
        setProgramadaPorDia((actuales) => ({ ...actuales, [dia]: actualizada }))
      } else {
        const creada = await crearRutinaProgramada({ dia_semana: dia, rutina_id: Number(valor) })
        setProgramadaPorDia((actuales) => ({ ...actuales, [dia]: creada }))
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setGuardandoDia(null)
    }
  }

  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      <EntrenamientoTabs />

      <PageHeader
        title="Horario semanal"
        description="Asigna qué rutina toca cada día. El calendario se rellena solo a partir de este patrón."
      />

      {cargando && <p className="mt-6 text-ink-muted">Cargando...</p>}

      {error && (
        <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      {!cargando && rutinas.length === 0 && (
        <div className="mt-6">
          <EmptyState
            title="Todavía no hay rutinas"
            description="Crea al menos una rutina en la pestaña Rutinas antes de poder programarla en el horario."
          />
        </div>
      )}

      {!cargando && rutinas.length > 0 && (
        <Card className="mt-6 divide-y divide-border overflow-hidden">
          {DIAS_SEMANA.map((dia) => (
            <div key={dia} className="flex items-center justify-between gap-3 px-4 py-3.5">
              <span className="font-medium text-ink">{DIA_SEMANA_ETIQUETA[dia]}</span>
              <select
                value={programadaPorDia[dia]?.rutina_id ?? ''}
                onChange={(e) => manejarCambio(dia, e.target.value)}
                disabled={guardandoDia === dia}
                className={`w-48 ${CAMPO} py-1.5`}
              >
                <option value="">Sin asignar</option>
                {rutinas.map((rutina) => (
                  <option key={rutina.id} value={rutina.id}>
                    {rutina.nombre}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </Card>
      )}
    </main>
  )
}
