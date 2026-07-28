import { useEffect, useState } from 'react'
import { getRutina } from '../api/rutinas'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { EmptyState } from './ui/EmptyState'
import { PageHeader } from './ui/PageHeader'

export function RutinaDetalle({ rutinaId, onVolver }) {
  const [rutina, setRutina] = useState(null)
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    setCargando(true)
    getRutina(rutinaId)
      .then(setRutina)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }, [rutinaId])

  return (
    <div>
      <Button variant="ghost" onClick={onVolver} className="-ml-3">
        ← Volver a rutinas
      </Button>

      {cargando && <p className="mt-6 text-ink-muted">Cargando...</p>}

      {error && (
        <p className="mt-6 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      {rutina && (
        <>
          <div className="mt-4">
            <PageHeader title={rutina.nombre} />
          </div>

          {rutina.ejercicios.length === 0 && (
            <div className="mt-6">
              <EmptyState
                title="Sin ejercicios todavía"
                description="Esta rutina no tiene ejercicios asignados."
              />
            </div>
          )}

          {rutina.ejercicios.length > 0 && (
            <Card className="mt-6 divide-y divide-border overflow-hidden">
              {[...rutina.ejercicios]
                .sort((a, b) => a.orden - b.orden)
                .map((item) => (
                  <div
                    key={`${item.ejercicio.id}-${item.orden}`}
                    className="flex items-center justify-between px-4 py-3.5"
                  >
                    <span className="font-medium text-ink">
                      <span className="mr-2 text-ink-muted">{item.orden}.</span>
                      {item.ejercicio.nombre}
                    </span>
                    <span className="font-heading text-sm font-semibold text-accent">
                      {item.series_objetivo} × {item.repeticiones_objetivo}
                    </span>
                  </div>
                ))}
            </Card>
          )}
        </>
      )}
    </div>
  )
}
