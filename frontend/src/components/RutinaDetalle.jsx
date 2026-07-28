import { useEffect, useState } from 'react'
import { getRutina } from '../api/rutinas'

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
      <button
        type="button"
        onClick={onVolver}
        className="text-sm font-medium text-gray-600 hover:underline"
      >
        ← Volver a rutinas
      </button>

      {cargando && <p className="mt-6 text-gray-500">Cargando...</p>}

      {error && (
        <p className="mt-6 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>
      )}

      {rutina && (
        <>
          <h1 className="mt-4 text-2xl font-semibold text-gray-900">{rutina.nombre}</h1>

          {rutina.ejercicios.length === 0 && (
            <p className="mt-6 text-gray-500">Esta rutina todavía no tiene ejercicios.</p>
          )}

          {rutina.ejercicios.length > 0 && (
            <ul className="mt-6 divide-y divide-gray-200 rounded-md border border-gray-200">
              {[...rutina.ejercicios]
                .sort((a, b) => a.orden - b.orden)
                .map((item) => (
                  <li key={`${item.ejercicio.id}-${item.orden}`} className="p-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">
                        {item.orden}. {item.ejercicio.nombre}
                      </span>
                      <span className="text-sm text-gray-500">
                        {item.series_objetivo} x {item.repeticiones_objetivo}
                      </span>
                    </div>
                  </li>
                ))}
            </ul>
          )}
        </>
      )}
    </div>
  )
}
