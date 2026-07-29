import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui/Button'

const SECCIONES = [
  { to: '/', etiqueta: 'Inicio', prefijo: '/' },
  { to: '/entrenamiento/rutinas', etiqueta: 'Entrenamiento', prefijo: '/entrenamiento' },
  { to: '/alimentacion', etiqueta: 'Alimentación', prefijo: '/alimentacion' },
]

export function LayoutPrincipal() {
  const { usuario, logout } = useAuth()
  const location = useLocation()

  const secciones =
    usuario.rol === 'admin'
      ? [...SECCIONES, { to: '/catalogo', etiqueta: 'Catálogo', prefijo: '/catalogo' }]
      : SECCIONES

  return (
    <div>
      <div className="border-b border-border bg-surface/40">
        <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-3 px-8 py-3">
          <nav className="flex gap-1 rounded-full border border-border bg-surface p-1">
            {secciones.map(({ to, etiqueta, prefijo }) => {
              // "Inicio" solo se marca activo en la raíz exacta; el resto se
              // marca activo para cualquier sub-ruta suya (ej. Entrenamiento
              // sigue resaltado en Rutinas/Horario/Historial).
              const activa =
                prefijo === '/' ? location.pathname === '/' : location.pathname.startsWith(prefijo)
              return (
                <Link
                  key={to}
                  to={to}
                  className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                    activa ? 'bg-accent text-accent-foreground' : 'text-ink-muted hover:text-ink'
                  }`}
                >
                  {etiqueta}
                </Link>
              )
            })}
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/perfil"
              className="inline-flex items-center justify-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-canvas"
            >
              Hola, {usuario.nombre}
            </Link>
            <Button variant="ghostDanger" onClick={logout}>
              Cerrar sesión
            </Button>
          </div>
        </div>
      </div>

      <Outlet />
    </div>
  )
}
