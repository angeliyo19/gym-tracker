import esLocale from '@fullcalendar/core/locales/es'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCalendario } from '../api/calendario'
import { getRutinas } from '../api/rutinas'
import { actualizarSesion } from '../api/sesiones'
import { Button } from '../components/ui/Button'
import { Modal } from '../components/ui/Modal'
import { PageHeader } from '../components/ui/PageHeader'
import { formatearFecha } from '../utils/fecha'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

function formatearFechaLocal(fecha) {
  const anio = fecha.getFullYear()
  const mes = String(fecha.getMonth() + 1).padStart(2, '0')
  const dia = String(fecha.getDate()).padStart(2, '0')
  return `${anio}-${mes}-${dia}`
}

function sesionAEvento(sesion) {
  // Una sesión ya empezada (tiene hora_inicio, aunque no se haya finalizado
  // todavía) se muestra como evento con hora concreta; las que aún no se han
  // tocado siguen mostrándose como "todo el día", ya que solo sabemos la
  // fecha objetivo, no una hora real.
  const empezada = sesion.hora_inicio != null
  const color = sesion.completada ? 'var(--success)' : 'var(--pendiente)'
  const colorTexto = sesion.completada
    ? 'var(--success-foreground)'
    : 'var(--pendiente-foreground)'
  return {
    id: String(sesion.id),
    title: sesion.rutina.nombre,
    start: empezada ? sesion.hora_inicio : sesion.fecha,
    end: empezada && sesion.hora_fin ? sesion.hora_fin : undefined,
    allDay: !empezada,
    startEditable: !sesion.completada,
    durationEditable: false,
    backgroundColor: color,
    borderColor: color,
    textColor: colorTexto,
    extendedProps: { sesion },
  }
}

export function CalendarioPage() {
  const navigate = useNavigate()
  const [eventos, setEventos] = useState([])
  const [rutinas, setRutinas] = useState([])
  const [error, setError] = useState(null)

  const [sesionSeleccionada, setSesionSeleccionada] = useState(null)
  const [modoModal, setModoModal] = useState('acciones')
  const [nuevaRutinaId, setNuevaRutinaId] = useState('')
  const [guardandoCambio, setGuardandoCambio] = useState(false)
  const [errorModal, setErrorModal] = useState(null)

  useEffect(() => {
    getRutinas()
      .then(setRutinas)
      .catch((err) => setError(err.message))
  }, [])

  async function cargarRango(desde, hasta) {
    setError(null)
    try {
      const sesiones = await getCalendario(desde, hasta)
      setEventos(sesiones.map(sesionAEvento))
    } catch (err) {
      setError(err.message)
    }
  }

  function manejarCambioRango(info) {
    const desde = formatearFechaLocal(info.start)
    const ultimoDiaVisible = new Date(info.end)
    ultimoDiaVisible.setDate(ultimoDiaVisible.getDate() - 1)
    const hasta = formatearFechaLocal(ultimoDiaVisible)
    cargarRango(desde, hasta)
  }

  function manejarClickEvento(info) {
    const sesion = info.event.extendedProps.sesion
    if (sesion.completada) {
      navigate(`/entrenamiento/sesiones/${sesion.id}`)
      return
    }
    setErrorModal(null)
    setNuevaRutinaId(String(sesion.rutina.id))
    setSesionSeleccionada(sesion)
    setModoModal('acciones')
  }

  async function manejarSoltarEvento(info) {
    const sesion = info.event.extendedProps.sesion
    if (sesion.completada) {
      info.revert()
      return
    }
    const nuevaFecha = formatearFechaLocal(info.event.start)
    try {
      const actualizada = await actualizarSesion(sesion.id, { fecha: nuevaFecha })
      setEventos((actuales) =>
        actuales.map((evento) =>
          evento.id === String(actualizada.id)
            ? sesionAEvento({ ...sesion, ...actualizada })
            : evento,
        ),
      )
    } catch (err) {
      setError(err.message)
      info.revert()
    }
  }

  function cerrarModal() {
    setSesionSeleccionada(null)
    setErrorModal(null)
  }

  function manejarIniciar() {
    navigate(`/entrenamiento/sesiones/${sesionSeleccionada.id}`)
  }

  async function manejarGuardarCambioRutina() {
    setErrorModal(null)
    setGuardandoCambio(true)
    try {
      const actualizada = await actualizarSesion(sesionSeleccionada.id, {
        rutina_id: Number(nuevaRutinaId),
      })
      const rutina = rutinas.find((r) => r.id === Number(nuevaRutinaId))
      setEventos((actuales) =>
        actuales.map((evento) =>
          evento.id === String(actualizada.id)
            ? sesionAEvento({ ...actualizada, rutina })
            : evento,
        ),
      )
      cerrarModal()
    } catch (err) {
      setErrorModal(err.message)
    } finally {
      setGuardandoCambio(false)
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-8 py-10">
      <PageHeader
        title="Calendario"
        description="Verde: completada. Gris: pendiente. Arrastra una sesión pendiente para cambiarla de día."
        action={
          <Button variant="secondary" onClick={() => navigate('/entrenamiento/horario')}>
            Horario semanal
          </Button>
        }
      />

      {error && (
        <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      <div className="calendario-tema mt-6">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay',
          }}
          locale={esLocale}
          height="auto"
          editable
          events={eventos}
          eventClick={manejarClickEvento}
          eventDrop={manejarSoltarEvento}
          datesSet={manejarCambioRango}
        />
      </div>

      {sesionSeleccionada && modoModal === 'acciones' && (
        <Modal title={formatearFecha(sesionSeleccionada.fecha)} onClose={cerrarModal}>
          <p className="text-sm text-ink-muted">
            Rutina: <span className="font-medium text-ink">{sesionSeleccionada.rutina.nombre}</span>
          </p>
          <div className="mt-5 flex flex-col gap-2">
            <Button variant="primary" onClick={manejarIniciar}>
              Iniciar sesión
            </Button>
            <Button variant="secondary" onClick={() => setModoModal('cambiar-rutina')}>
              Cambiar rutina de este día
            </Button>
          </div>
        </Modal>
      )}

      {sesionSeleccionada && modoModal === 'cambiar-rutina' && (
        <Modal title={formatearFecha(sesionSeleccionada.fecha)} onClose={cerrarModal}>
          <p className="text-sm text-ink-muted">
            Solo afecta a este día. El horario semanal no cambia.
          </p>

          <select
            value={nuevaRutinaId}
            onChange={(e) => setNuevaRutinaId(e.target.value)}
            className={`mt-4 block w-full ${CAMPO}`}
          >
            {rutinas.map((rutina) => (
              <option key={rutina.id} value={rutina.id}>
                {rutina.nombre}
              </option>
            ))}
          </select>

          {errorModal && (
            <p className="mt-3 rounded-lg bg-red-500/10 p-2 text-xs text-red-500">{errorModal}</p>
          )}

          <div className="mt-5 flex gap-2">
            <Button variant="primary" onClick={manejarGuardarCambioRutina} disabled={guardandoCambio}>
              {guardandoCambio ? 'Guardando...' : 'Guardar'}
            </Button>
            <Button variant="ghost" onClick={() => setModoModal('acciones')}>
              Volver
            </Button>
          </div>
        </Modal>
      )}
    </main>
  )
}
