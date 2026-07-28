import { useEffect, useState } from 'react'
import { getRutinas } from '../api/rutinas'
import { UsuarioSelector } from '../components/UsuarioSelector'
import { RutinasList } from '../components/RutinasList'
import { RutinaForm } from '../components/RutinaForm'
import { RutinaDetalle } from '../components/RutinaDetalle'

export function RutinasPage() {
  const [usuarioActivoId, setUsuarioActivoId] = useState(null)
  const [vista, setVista] = useState('lista')
  const [rutinaSeleccionadaId, setRutinaSeleccionadaId] = useState(null)
  const [rutinas, setRutinas] = useState([])
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  function cargarRutinas() {
    setCargando(true)
    getRutinas()
      .then(setRutinas)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }

  useEffect(cargarRutinas, [])

  const rutinasDelUsuario = rutinas.filter((rutina) => rutina.usuario_id === usuarioActivoId)

  return (
    <main className="mx-auto max-w-xl p-8">
      <UsuarioSelector usuarioId={usuarioActivoId} onChange={setUsuarioActivoId} />

      {!usuarioActivoId && (
        <p className="mt-6 text-gray-500">Selecciona un usuario para ver sus rutinas.</p>
      )}

      {usuarioActivoId && vista === 'detalle' && (
        <div className="mt-6">
          <RutinaDetalle rutinaId={rutinaSeleccionadaId} onVolver={() => setVista('lista')} />
        </div>
      )}

      {usuarioActivoId && vista === 'nueva' && (
        <div className="mt-6">
          <h1 className="text-2xl font-semibold text-gray-900">Nueva rutina</h1>
          <RutinaForm
            usuarioId={usuarioActivoId}
            onCancel={() => setVista('lista')}
            onCreated={() => {
              cargarRutinas()
              setVista('lista')
            }}
          />
        </div>
      )}

      {usuarioActivoId && vista === 'lista' && (
        <div className="mt-6">
          {cargando && <p className="text-gray-500">Cargando...</p>}

          {error && (
            <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>
          )}

          {!cargando && !error && (
            <RutinasList
              rutinas={rutinasDelUsuario}
              onNew={() => setVista('nueva')}
              onSelect={(id) => {
                setRutinaSeleccionadaId(id)
                setVista('detalle')
              }}
            />
          )}
        </div>
      )}
    </main>
  )
}
