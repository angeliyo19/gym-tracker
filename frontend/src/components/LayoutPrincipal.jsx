import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui/Button'

const SECCIONES = [
  { to: '/', etiqueta: 'Inicio', exacta: true },
  { to: '/entrenamiento/rutinas', etiqueta: 'Entrenamiento' },
  { to: '/alimentacion', etiqueta: 'Alimentación' },
]

export function LayoutPrincipal() {
  const { usuario, logout } = useAuth()

  return (
    <div>
      <div className="border-b border-border bg-surface/40">
        <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-3 px-8 py-3">
          <nav className="flex gap-1 rounded-full border border-border bg-surface p-1">
            {SECCIONES.map(({ to, etiqueta, exacta }) => (
              <NavLink
                key={to}
                to={to}
                end={exacta}
                className={({ isActive }) =>
                  `rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-accent text-accent-foreground'
                      : 'text-ink-muted hover:text-ink'
                  }`
                }
              >
                {etiqueta}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <span className="text-sm text-ink-muted">Hola, {usuario.nombre}</span>
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
