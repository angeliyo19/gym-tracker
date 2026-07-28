import { useEffect, useState } from 'react'
import { getRutinas } from '../api/rutinas'
import { RutinasList } from '../components/RutinasList'
import { RutinaForm } from '../components/RutinaForm'
import { RutinaDetalle } from '../components/RutinaDetalle'
import { PageHeader } from '../components/ui/PageHeader'

export function RutinasPage() {
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

  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      {vista === 'detalle' && (
        <RutinaDetalle rutinaId={rutinaSeleccionadaId} onVolver={() => setVista('lista')} />
      )}

      {vista === 'nueva' && (
        <div>
          <PageHeader
            title="Nueva rutina"
            description="Define su nombre y sus ejercicios objetivo."
          />
          <RutinaForm
            onCancel={() => setVista('lista')}
            onCreated={() => {
              cargarRutinas()
              setVista('lista')
            }}
          />
        </div>
      )}

      {vista === 'lista' && (
        <div>
          {cargando && <p className="text-ink-muted">Cargando...</p>}

          {error && (
            <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
          )}

          {!cargando && !error && (
            <RutinasList
              rutinas={rutinas}
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
