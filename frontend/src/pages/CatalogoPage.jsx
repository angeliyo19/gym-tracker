import { useEffect, useState } from 'react'
import {
  actualizarEjercicio,
  crearEjercicio,
  eliminarEjercicio,
  getEjercicios,
} from '../api/ejercicios'
import {
  actualizarGrupoMuscular,
  crearGrupoMuscular,
  eliminarGrupoMuscular,
  getGruposMusculares,
} from '../api/gruposMusculares'
import { useAuth } from '../context/AuthContext'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { EmptyState } from '../components/ui/EmptyState'
import { Modal } from '../components/ui/Modal'
import { PageHeader } from '../components/ui/PageHeader'

const CAMPO =
  'rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink ' +
  'focus:outline-none focus:ring-2 focus:ring-accent'

export function CatalogoPage() {
  const { usuario } = useAuth()
  const esAdmin = usuario?.rol === 'admin'

  const [ejercicios, setEjercicios] = useState([])
  const [grupos, setGrupos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const [modalGrupo, setModalGrupo] = useState(null)
  const [nombreGrupo, setNombreGrupo] = useState('')
  const [guardandoGrupo, setGuardandoGrupo] = useState(false)
  const [errorGrupo, setErrorGrupo] = useState(null)

  const [modalEjercicio, setModalEjercicio] = useState(null)
  const [nombreEjercicio, setNombreEjercicio] = useState('')
  const [tipoEjercicio, setTipoEjercicio] = useState('compuesto')
  const [gruposSeleccionados, setGruposSeleccionados] = useState({})
  const [guardandoEjercicio, setGuardandoEjercicio] = useState(false)
  const [errorEjercicio, setErrorEjercicio] = useState(null)

  function cargar() {
    setCargando(true)
    return Promise.all([getEjercicios(), getGruposMusculares()])
      .then(([ejerciciosData, gruposData]) => {
        setEjercicios(ejerciciosData)
        setGrupos(gruposData)
      })
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }

  useEffect(() => {
    cargar()
  }, [])

  // --- Grupos musculares ---

  function abrirNuevoGrupo() {
    setNombreGrupo('')
    setErrorGrupo(null)
    setModalGrupo('nuevo')
  }

  function abrirEditarGrupo(grupo) {
    setNombreGrupo(grupo.nombre)
    setErrorGrupo(null)
    setModalGrupo(grupo)
  }

  async function guardarGrupo(evento) {
    evento.preventDefault()
    setErrorGrupo(null)
    setGuardandoGrupo(true)
    try {
      if (modalGrupo === 'nuevo') {
        await crearGrupoMuscular({ nombre: nombreGrupo })
      } else {
        await actualizarGrupoMuscular(modalGrupo.id, { nombre: nombreGrupo })
      }
      await cargar()
      setModalGrupo(null)
    } catch (err) {
      setErrorGrupo(err.message)
    } finally {
      setGuardandoGrupo(false)
    }
  }

  async function manejarEliminarGrupo(grupo) {
    setError(null)
    try {
      await eliminarGrupoMuscular(grupo.id)
      await cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  // --- Ejercicios ---

  function abrirNuevoEjercicio() {
    setNombreEjercicio('')
    setTipoEjercicio('compuesto')
    setGruposSeleccionados({})
    setErrorEjercicio(null)
    setModalEjercicio('nuevo')
  }

  function abrirEditarEjercicio(ejercicio) {
    setNombreEjercicio(ejercicio.nombre)
    setTipoEjercicio(ejercicio.tipo)
    setGruposSeleccionados(
      Object.fromEntries(
        ejercicio.grupos_musculares.map((asociacion) => [
          asociacion.grupo_muscular.id,
          { esPrincipal: asociacion.es_principal },
        ]),
      ),
    )
    setErrorEjercicio(null)
    setModalEjercicio(ejercicio)
  }

  function alternarGrupoSeleccionado(grupoId) {
    setGruposSeleccionados((actuales) => {
      if (actuales[grupoId]) {
        const { [grupoId]: _quitado, ...resto } = actuales
        return resto
      }
      return { ...actuales, [grupoId]: { esPrincipal: false } }
    })
  }

  function alternarPrincipal(grupoId) {
    setGruposSeleccionados((actuales) => ({
      ...actuales,
      [grupoId]: { esPrincipal: !actuales[grupoId].esPrincipal },
    }))
  }

  async function guardarEjercicio(evento) {
    evento.preventDefault()
    setErrorEjercicio(null)
    setGuardandoEjercicio(true)
    try {
      const datos = {
        nombre: nombreEjercicio,
        tipo: tipoEjercicio,
        grupos_musculares: Object.entries(gruposSeleccionados).map(
          ([grupoId, { esPrincipal }]) => ({
            grupo_muscular_id: Number(grupoId),
            es_principal: esPrincipal,
          }),
        ),
      }
      if (modalEjercicio === 'nuevo') {
        await crearEjercicio(datos)
      } else {
        await actualizarEjercicio(modalEjercicio.id, datos)
      }
      await cargar()
      setModalEjercicio(null)
    } catch (err) {
      setErrorEjercicio(err.message)
    } finally {
      setGuardandoEjercicio(false)
    }
  }

  async function manejarEliminarEjercicio(ejercicio) {
    setError(null)
    try {
      await eliminarEjercicio(ejercicio.id)
      await cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      <PageHeader
        title="Catálogo"
        description="Ejercicios y grupos musculares disponibles para las rutinas."
      />

      {cargando && <p className="mt-6 text-ink-muted">Cargando...</p>}

      {error && (
        <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">{error}</p>
      )}

      {!cargando && (
        <>
          <div className="mt-8">
            <div className="flex items-center justify-between">
              <h2 className="font-heading text-lg font-semibold text-ink">Grupos musculares</h2>
              {esAdmin && (
                <Button variant="secondary" onClick={abrirNuevoGrupo}>
                  + Nuevo grupo
                </Button>
              )}
            </div>

            {grupos.length === 0 && (
              <div className="mt-4">
                <EmptyState
                  title="Todavía no hay grupos musculares"
                  description="Añade el primero para poder asociarlo a ejercicios."
                />
              </div>
            )}

            {grupos.length > 0 && (
              <Card className="mt-4 divide-y divide-border overflow-hidden">
                {grupos.map((grupo) => (
                  <div
                    key={grupo.id}
                    className="flex items-center justify-between gap-3 px-4 py-3"
                  >
                    <span className="font-medium text-ink">{grupo.nombre}</span>
                    {esAdmin && (
                      <div className="flex gap-2">
                        <Button variant="ghost" onClick={() => abrirEditarGrupo(grupo)}>
                          Editar
                        </Button>
                        <Button variant="danger" onClick={() => manejarEliminarGrupo(grupo)}>
                          Eliminar
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </Card>
            )}
          </div>

          <div className="mt-10">
            <div className="flex items-center justify-between">
              <h2 className="font-heading text-lg font-semibold text-ink">Ejercicios</h2>
              {esAdmin && (
                <Button variant="secondary" onClick={abrirNuevoEjercicio}>
                  + Nuevo ejercicio
                </Button>
              )}
            </div>

            {ejercicios.length === 0 && (
              <div className="mt-4">
                <EmptyState
                  title="Todavía no hay ejercicios"
                  description="Añade el primero para poder usarlo en tus rutinas."
                />
              </div>
            )}

            {ejercicios.length > 0 && (
              <Card className="mt-4 divide-y divide-border overflow-hidden">
                {ejercicios.map((ejercicio) => (
                  <div key={ejercicio.id} className="px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <span className="font-medium text-ink">{ejercicio.nombre}</span>
                        <span className="ml-2 text-xs text-ink-muted">{ejercicio.tipo}</span>
                      </div>
                      {esAdmin && (
                        <div className="flex gap-2">
                          <Button variant="ghost" onClick={() => abrirEditarEjercicio(ejercicio)}>
                            Editar
                          </Button>
                          <Button
                            variant="danger"
                            onClick={() => manejarEliminarEjercicio(ejercicio)}
                          >
                            Eliminar
                          </Button>
                        </div>
                      )}
                    </div>
                    {ejercicio.grupos_musculares.length > 0 && (
                      <p className="mt-1 text-xs text-ink-muted">
                        {ejercicio.grupos_musculares
                          .map(
                            (asociacion) =>
                              asociacion.grupo_muscular.nombre +
                              (asociacion.es_principal ? ' (principal)' : ''),
                          )
                          .join(', ')}
                      </p>
                    )}
                  </div>
                ))}
              </Card>
            )}
          </div>
        </>
      )}

      {modalGrupo && (
        <Modal
          title={modalGrupo === 'nuevo' ? 'Nuevo grupo muscular' : 'Editar grupo muscular'}
          onClose={() => setModalGrupo(null)}
        >
          <form onSubmit={guardarGrupo}>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Nombre</label>
            <input
              type="text"
              required
              placeholder="Ej. pecho"
              value={nombreGrupo}
              onChange={(e) => setNombreGrupo(e.target.value)}
              className={`block w-full ${CAMPO}`}
            />

            {errorGrupo && (
              <p className="mt-3 rounded-lg bg-red-500/10 p-2 text-xs text-red-500">
                {errorGrupo}
              </p>
            )}

            <div className="mt-5 flex gap-2">
              <Button type="submit" variant="primary" disabled={guardandoGrupo}>
                {guardandoGrupo ? 'Guardando...' : 'Guardar'}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setModalGrupo(null)}>
                Cancelar
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {modalEjercicio && (
        <Modal
          title={modalEjercicio === 'nuevo' ? 'Nuevo ejercicio' : 'Editar ejercicio'}
          onClose={() => setModalEjercicio(null)}
        >
          <form onSubmit={guardarEjercicio}>
            <label className="mb-1.5 block text-sm font-medium text-ink-muted">Nombre</label>
            <input
              type="text"
              required
              placeholder="Ej. Press banca"
              value={nombreEjercicio}
              onChange={(e) => setNombreEjercicio(e.target.value)}
              className={`block w-full ${CAMPO}`}
            />

            <label className="mb-1.5 mt-4 block text-sm font-medium text-ink-muted">Tipo</label>
            <select
              value={tipoEjercicio}
              onChange={(e) => setTipoEjercicio(e.target.value)}
              className={`block w-full ${CAMPO}`}
            >
              <option value="compuesto">Compuesto</option>
              <option value="aislamiento">Aislamiento</option>
            </select>

            {grupos.length > 0 && (
              <div className="mt-4">
                <span className="mb-1.5 block text-sm font-medium text-ink-muted">
                  Grupos musculares
                </span>
                <div className="max-h-40 space-y-1.5 overflow-y-auto rounded-lg border border-border p-2">
                  {grupos.map((grupo) => {
                    const seleccionado = gruposSeleccionados[grupo.id]
                    return (
                      <div key={grupo.id} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          id={`grupo-${grupo.id}`}
                          checked={Boolean(seleccionado)}
                          onChange={() => alternarGrupoSeleccionado(grupo.id)}
                        />
                        <label htmlFor={`grupo-${grupo.id}`} className="flex-1 text-ink">
                          {grupo.nombre}
                        </label>
                        {seleccionado && (
                          <label className="flex items-center gap-1 text-xs text-ink-muted">
                            <input
                              type="checkbox"
                              checked={seleccionado.esPrincipal}
                              onChange={() => alternarPrincipal(grupo.id)}
                            />
                            Principal
                          </label>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {errorEjercicio && (
              <p className="mt-3 rounded-lg bg-red-500/10 p-2 text-xs text-red-500">
                {errorEjercicio}
              </p>
            )}

            <div className="mt-5 flex gap-2">
              <Button type="submit" variant="primary" disabled={guardandoEjercicio}>
                {guardandoEjercicio ? 'Guardando...' : 'Guardar'}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setModalEjercicio(null)}>
                Cancelar
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </main>
  )
}
