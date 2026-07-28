import { useEffect, useState } from 'react'
import { getEjercicios } from '../api/ejercicios'
import { createRutina } from '../api/rutinas'

function nuevaFila(ejercicios) {
  return {
    ejercicio_id: ejercicios[0]?.id ?? '',
    orden: 1,
    series_objetivo: 3,
    repeticiones_objetivo: 10,
  }
}

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
    return <p className="mt-6 text-gray-500">Cargando...</p>
  }

  if (ejercicios.length === 0) {
    return (
      <p className="mt-6 rounded-md bg-yellow-50 p-3 text-sm text-yellow-800">
        Hace falta al menos un ejercicio en el catálogo antes de crear una rutina.
      </p>
    )
  }

  return (
    <form onSubmit={manejarSubmit} className="mt-6 space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700">Nombre</label>
        <input
          type="text"
          required
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
      </div>

      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-gray-700">Ejercicios</h2>
          <button
            type="button"
            onClick={añadirFila}
            className="text-sm font-medium text-gray-900 hover:underline"
          >
            + Añadir ejercicio
          </button>
        </div>

        <div className="mt-2 space-y-3">
          {filas.map((fila, indice) => (
            <div
              key={indice}
              className="grid grid-cols-12 gap-2 rounded-md border border-gray-200 p-3"
            >
              <select
                value={fila.ejercicio_id}
                onChange={(e) => actualizarFila(indice, 'ejercicio_id', e.target.value)}
                className="col-span-5 rounded-md border border-gray-300 px-2 py-1 text-sm"
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
                className="col-span-2 rounded-md border border-gray-300 px-2 py-1 text-sm"
              />
              <input
                type="number"
                min={1}
                value={fila.series_objetivo}
                onChange={(e) => actualizarFila(indice, 'series_objetivo', e.target.value)}
                title="Series objetivo"
                className="col-span-2 rounded-md border border-gray-300 px-2 py-1 text-sm"
              />
              <input
                type="number"
                min={1}
                value={fila.repeticiones_objetivo}
                onChange={(e) =>
                  actualizarFila(indice, 'repeticiones_objetivo', e.target.value)
                }
                title="Repeticiones objetivo"
                className="col-span-2 rounded-md border border-gray-300 px-2 py-1 text-sm"
              />

              <button
                type="button"
                onClick={() => quitarFila(indice)}
                className="col-span-1 text-sm text-red-600 hover:underline"
              >
                Quitar
              </button>
            </div>
          ))}
        </div>
        <p className="mt-1 text-xs text-gray-400">Orden / Series / Repeticiones objetivo</p>
      </div>

      {error && (
        <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={enviando}
          className="rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          {enviando ? 'Guardando...' : 'Crear rutina'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
