import { useState } from 'react'
import { crearSerie, eliminarSerie } from '../api/series'
import { formatearFecha } from '../utils/fecha'
import { Button } from './ui/Button'
import { Card } from './ui/Card'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

function nuevaFila() {
  return {
    id: null,
    peso: '',
    repeticiones: '',
    guardando: false,
    guardada: false,
    eliminando: false,
    error: null,
  }
}

function filaDesdeSerieGuardada(serie) {
  return {
    id: serie.id,
    peso: String(serie.peso),
    repeticiones: String(serie.repeticiones),
    guardando: false,
    guardada: true,
    eliminando: false,
    error: null,
  }
}

function filasIniciales(seriesObjetivo, seriesGuardadas) {
  const filasGuardadas = seriesGuardadas.map(filaDesdeSerieGuardada)
  const faltan = Math.max(seriesObjetivo, 1) - filasGuardadas.length
  const filasVacias = Array.from({ length: Math.max(faltan, 0) }, nuevaFila)
  return [...filasGuardadas, ...filasVacias]
}

export function EjercicioEnVivo({
  sesionId,
  ejercicio,
  seriesObjetivo,
  repeticionesObjetivo,
  referencia,
  seriesGuardadas = [],
  soloLectura = false,
}) {
  const [filas, setFilas] = useState(() => filasIniciales(seriesObjetivo, seriesGuardadas))

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
      const serie = await crearSerie(sesionId, {
        ejercicio_id: ejercicio.id,
        peso: Number(fila.peso),
        repeticiones: Number(fila.repeticiones),
      })
      actualizarFila(indice, { guardando: false, guardada: true, id: serie.id })
    } catch (err) {
      actualizarFila(indice, { guardando: false, error: err.message })
    }
  }

  async function eliminarFila(indice) {
    const fila = filas[indice]
    if (!fila.id) return

    actualizarFila(indice, { eliminando: true, error: null })
    try {
      await eliminarSerie(sesionId, fila.id)
      setFilas((actuales) => actuales.filter((_, i) => i !== indice))
    } catch (err) {
      actualizarFila(indice, { eliminando: false, error: err.message })
    }
  }

  const filasVisibles = soloLectura ? filas.filter((fila) => fila.guardada) : filas

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-heading text-lg font-semibold text-ink">{ejercicio.nombre}</h2>
        <span className="whitespace-nowrap rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
          Objetivo: {seriesObjetivo} × {repeticionesObjetivo}
        </span>
      </div>

      {referencia && !soloLectura && (
        <p className="mt-1 text-xs text-ink-muted">
          Última vez ({formatearFecha(referencia.fecha)}): {referencia.peso} kg ×{' '}
          {referencia.repeticiones}
        </p>
      )}

      <div className="mt-4 space-y-2">
        {filasVisibles.length === 0 && soloLectura && (
          <p className="text-sm text-ink-muted">No se registraron series.</p>
        )}

        {filasVisibles.map((fila, indice) => (
          <div key={fila.id ?? `nueva-${indice}`} className="flex items-center gap-2">
            <span className="w-5 text-sm text-ink-muted">{indice + 1}.</span>

            {soloLectura ? (
              <span className="text-sm text-ink">
                {fila.peso} kg × {fila.repeticiones}
              </span>
            ) : (
              <>
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
                  <>
                    <span className="text-sm font-medium text-accent">✓ Guardada</span>
                    <Button
                      type="button"
                      variant="danger"
                      onClick={() => eliminarFila(indice)}
                      disabled={fila.eliminando}
                    >
                      {fila.eliminando ? 'Eliminando...' : 'Eliminar'}
                    </Button>
                  </>
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
              </>
            )}

            {fila.error && <span className="text-xs text-red-500">{fila.error}</span>}
          </div>
        ))}
      </div>

      {!soloLectura && (
        <button
          type="button"
          onClick={añadirFila}
          className="mt-3 text-sm font-medium text-accent hover:text-accent-hover"
        >
          + Añadir serie
        </button>
      )}
    </Card>
  )
}
