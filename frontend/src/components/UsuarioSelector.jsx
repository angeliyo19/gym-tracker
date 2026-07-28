import { useEffect, useState } from 'react'
import { getUsuarios } from '../api/usuarios'

export function UsuarioSelector({ usuarioId, onChange }) {
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getUsuarios()
      .then((data) => {
        setUsuarios(data)
        if (data.length > 0 && !usuarioId) {
          onChange(data[0].id)
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
    // Solo se carga una vez al montar; el efecto no debe repetirse al cambiar usuarioId.
    // eslint-disable-next-line
  }, [])

  if (cargando) {
    return <p className="text-sm text-ink-muted">Cargando usuarios...</p>
  }

  if (error) {
    return <p className="text-sm text-red-500">Error al cargar usuarios: {error}</p>
  }

  if (usuarios.length === 0) {
    return <p className="text-sm text-ink-muted">No hay usuarios todavía.</p>
  }

  return (
    <div className="flex items-center gap-3">
      <label htmlFor="usuario-activo" className="text-sm font-medium text-ink-muted">
        Usuario activo
      </label>
      <select
        id="usuario-activo"
        value={usuarioId ?? ''}
        onChange={(e) => onChange(Number(e.target.value))}
        className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-accent"
      >
        {usuarios.map((usuario) => (
          <option key={usuario.id} value={usuario.id}>
            {usuario.nombre}
          </option>
        ))}
      </select>
    </div>
  )
}
