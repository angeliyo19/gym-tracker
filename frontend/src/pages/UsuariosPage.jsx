import { useEffect, useState } from 'react'
import { getUsuarios } from '../api/usuarios'

export function UsuariosPage() {
  const [usuarios, setUsuarios] = useState([])
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    getUsuarios()
      .then(setUsuarios)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }, [])

  return (
    <main className="mx-auto max-w-xl p-8">
      <h1 className="text-2xl font-semibold text-gray-900">Usuarios</h1>
      <p className="mt-1 text-sm text-gray-500">
        Página de prueba: confirma la comunicación entre frontend y backend.
      </p>

      {cargando && <p className="mt-6 text-gray-500">Cargando...</p>}

      {error && (
        <p className="mt-6 rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al conectar con la API: {error}
        </p>
      )}

      {!cargando && !error && usuarios.length === 0 && (
        <p className="mt-6 text-gray-500">No hay usuarios todavía.</p>
      )}

      {!cargando && !error && usuarios.length > 0 && (
        <ul className="mt-6 divide-y divide-gray-200 rounded-md border border-gray-200">
          {usuarios.map((usuario) => (
            <li key={usuario.id} className="p-3">
              <p className="font-medium text-gray-900">{usuario.nombre}</p>
              <p className="text-sm text-gray-500">{usuario.email}</p>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
