import { useState } from 'react'
import { crearSerie } from '../api/series'
import { Button } from './ui/Button'
import { Card } from './ui/Card'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

function nuevaFila() {
  return { peso: '', repeticiones: '', guardando: false, guardada: false, error: null }
}

function formatearFecha(fechaIso) {
  const [anio, mes, dia] = fechaIso.split('-')
  return `${dia}/${mes}/${anio}`
}

export function EjercicioEnVivo({
  sesionId,
  ejercicio,
  seriesObjetivo,
  repeticionesObjetivo,
  referencia,
}) {
  const [filas, setFilas] = useState(() =>
    Array.from({ length: Math.max(seriesObjetivo, 1) }, nuevaFila),
  )

  function actualizarFila(indice, cambios) {
    setFilas((actuales) =>
      actuales.map((fila, i) => (i === indice ? { ...fila, ...cambios } : fila)),
    )
  }

  function añadirFila() {
    setFilas((actuales) => [...actuales, nuevaFila()])
  }

  async function guardarFila(indice) {
    const fila = filas[indice]
    if (!fila.peso || !fila.repeticiones) return

    actualizarFila(indice, { guardando: true, error: null })
    try {
      await crearSerie(sesionId, {
        ejercicio_id: ejercicio.id,
        peso: Number(fila.peso),
        repeticiones: Number(fila.repeticiones),
      })
      actualizarFila(indice, { guardando: false, guardada: true })
    } catch (err) {
      actualizarFila(indice, { guardando: false, error: err.message })
    }
  }

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-heading text-lg font-semibold text-ink">{ejercicio.nombre}</h2>
        <span className="whitespace-nowrap rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
          Objetivo: {seriesObjetivo} × {repeticionesObjetivo}
        </span>
      </div>

      {referencia && (
        <p className="mt-1 text-xs text-ink-muted">
          Última vez ({formatearFecha(referencia.fecha)}): {referencia.peso} kg ×{' '}
          {referencia.repeticiones}
        </p>
      )}

      <div className="mt-4 space-y-2">
        {filas.map((fila, indice) => (
          <div key={indice} className="flex items-center gap-2">
            <span className="w-5 text-sm text-ink-muted">{indice + 1}.</span>
            <input
              type="number"
              step="0.5"
              min={0}
              placeholder="Peso"
              value={fila.peso}
              disabled={fila.guardada}
              onChange={(e) => actualizarFila(indice, { peso: e.target.value })}
              className={`w-24 ${CAMPO}`}
            />
            <span className="text-ink-muted">×</span>
            <input
              type="number"
              min={0}
              placeholder="Reps"
              value={fila.repeticiones}
              disabled={fila.guardada}
              onChange={(e) => actualizarFila(indice, { repeticiones: e.target.value })}
              className={`w-20 ${CAMPO}`}
            />

            {fila.guardada ? (
              <span className="text-sm font-medium text-accent">✓ Guardada</span>
            ) : (
              <Button
                type="button"
                variant="secondary"
                onClick={() => guardarFila(indice)}
                disabled={fila.guardando || !fila.peso || !fila.repeticiones}
              >
                {fila.guardando ? 'Guardando...' : 'Guardar'}
              </Button>
            )}

            {fila.error && <span className="text-xs text-red-500">{fila.error}</span>}
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={añadirFila}
        className="mt-3 text-sm font-medium text-accent hover:text-accent-hover"
      >
        + Añadir serie
      </button>
    </Card>
  )
}
