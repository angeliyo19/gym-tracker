import { useEffect, useState } from 'react'
import { getRutinas } from '../api/rutinas'
import { UsuarioSelector } from '../components/UsuarioSelector'
import { RutinasList } from '../components/RutinasList'
import { RutinaForm } from '../components/RutinaForm'
import { RutinaDetalle } from '../components/RutinaDetalle'
import { PageHeader } from '../components/ui/PageHeader'

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
    <main className="mx-auto max-w-xl px-8 py-10">
      <UsuarioSelector usuarioId={usuarioActivoId} onChange={setUsuarioActivoId} />

      {!usuarioActivoId && (
        <p className="mt-6 text-ink-muted">Selecciona un usuario para ver sus rutinas.</p>
      )}

      {usuarioActivoId && vista === 'detalle' && (
        <div className="mt-8">
          <RutinaDetalle rutinaId={rutinaSeleccionadaId} onVolver={() => setVista('lista')} />
        </div>
      )}

      {usuarioActivoId && vista === 'nueva' && (
        <div className="mt-8">
          <PageHeader title="Nueva rutina" description="Define su nombre y sus ejercicios objetivo." />
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
        <div className="mt-8">
          {cargando && <p className="text-ink-muted">Cargando...</p>}

          {error && (
            <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
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
