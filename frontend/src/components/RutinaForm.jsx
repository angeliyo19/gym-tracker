import { useEffect, useState } from 'react'
import { getEjercicios } from '../api/ejercicios'
import { createRutina } from '../api/rutinas'
import { Button } from './ui/Button'
import { EmptyState } from './ui/EmptyState'

function nuevaFila(ejercicios) {
  return {
    ejercicio_id: ejercicios[0]?.id ?? '',
    orden: 1,
    series_objetivo: 3,
    repeticiones_objetivo: 10,
  }
}

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

export function RutinaForm({ usuarioId, onCreated, onCancel }) {
  const [ejercicios, setEjercicios] = useState([])
  const [cargandoCatalogo, setCargandoCatalogo] = useState(true)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  const [nombre, setNombre] = useState('')
  const [filas, setFilas] = useState([])

  useEffect(() => {
    getEjercicios()
      .then((ejerciciosData) => {
        setEjercicios(ejerciciosData)
        setFilas(ejerciciosData.length > 0 ? [nuevaFila(ejerciciosData)] : [])
      })
      .catch((err) => setError(err.message))
      .finally(() => setCargandoCatalogo(false))
  }, [])

  function actualizarFila(indice, campo, valor) {
    setFilas((actuales) =>
      actuales.map((fila, i) => (i === indice ? { ...fila, [campo]: valor } : fila)),
    )
  }

  function añadirFila() {
    setFilas((actuales) => [
      ...actuales,
      { ...nuevaFila(ejercicios), orden: actuales.length + 1 },
    ])
  }

  function quitarFila(indice) {
    setFilas((actuales) => actuales.filter((_, i) => i !== indice))
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      const rutina = await createRutina({
        nombre,
        usuario_id: usuarioId,
        ejercicios: filas.map((fila) => ({
          ejercicio_id: Number(fila.ejercicio_id),
          orden: Number(fila.orden),
          series_objetivo: Number(fila.series_objetivo),
          repeticiones_objetivo: Number(fila.repeticiones_objetivo),
        })),
      })
      onCreated(rutina)
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  if (cargandoCatalogo) {
    return <p className="mt-6 text-ink-muted">Cargando...</p>
  }

  if (ejercicios.length === 0) {
    return (
      <div className="mt-6">
        <EmptyState
          title="Falta un catálogo de ejercicios"
          description="Hace falta al menos un ejercicio antes de poder crear una rutina."
          action={
            <Button variant="secondary" onClick={onCancel}>
              Volver
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <form onSubmit={manejarSubmit} className="mt-6 space-y-6">
      <div>
        <label className="mb-1.5 block text-sm font-medium text-ink-muted">Nombre</label>
        <input
          type="text"
          required
          placeholder="Ej. Push day"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className={`block w-full ${CAMPO}`}
        />
      </div>

      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-ink-muted">Ejercicios</h2>
          <button
            type="button"
            onClick={añadirFila}
            className="text-sm font-medium text-accent hover:text-accent-hover"
          >
            + Añadir ejercicio
          </button>
        </div>

        <div className="mt-2 space-y-3">
          {filas.map((fila, indice) => (
            <div
              key={indice}
              className="grid grid-cols-12 items-center gap-2 rounded-xl border border-border bg-surface p-3"
            >
              <select
                value={fila.ejercicio_id}
                onChange={(e) => actualizarFila(indice, 'ejercicio_id', e.target.value)}
                className={`col-span-5 ${CAMPO} py-1.5`}
              >
                {ejercicios.map((ejercicio) => (
                  <option key={ejercicio.id} value={ejercicio.id}>
                    {ejercicio.nombre}
                  </option>
                ))}
              </select>

              <input
                type="number"
                min={1}
                value={fila.orden}
                onChange={(e) => actualizarFila(indice, 'orden', e.target.value)}
                title="Orden"
                className={`col-span-2 ${CAMPO} py-1.5`}
              />
              <input
                type="number"
                min={1}
                value={fila.series_objetivo}
                onChange={(e) => actualizarFila(indice, 'series_objetivo', e.target.value)}
                title="Series objetivo"
                className={`col-span-2 ${CAMPO} py-1.5`}
              />
              <input
                type="number"
                min={1}
                value={fila.repeticiones_objetivo}
                onChange={(e) =>
                  actualizarFila(indice, 'repeticiones_objetivo', e.target.value)
                }
                title="Repeticiones objetivo"
                className={`col-span-2 ${CAMPO} py-1.5`}
              />

              <button
                type="button"
                onClick={() => quitarFila(indice)}
                className="col-span-1 text-sm text-red-500 hover:text-red-400"
              >
                Quitar
              </button>
            </div>
          ))}
        </div>
        <p className="mt-1.5 text-xs text-ink-muted">Orden / Series / Repeticiones objetivo</p>
      </div>

      {error && (
        <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      <div className="flex gap-3">
        <Button type="submit" variant="primary" disabled={enviando}>
          {enviando ? 'Guardando...' : 'Crear rutina'}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    </form>
  )
}
