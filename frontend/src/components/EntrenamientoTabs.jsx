import { NavLink } from 'react-router-dom'

const PESTAÑAS = [
  { to: '/entrenamiento/rutinas', etiqueta: 'Rutinas' },
  { to: '/entrenamiento/horario', etiqueta: 'Horario' },
  { to: '/entrenamiento/calendario', etiqueta: 'Calendario' },
  { to: '/entrenamiento/historial', etiqueta: 'Historial' },
]

export function EntrenamientoTabs() {
  return (
    <div className="mb-6 flex gap-1 border-b border-border">
      {PESTAÑAS.map(({ to, etiqueta }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'border-accent text-accent'
                : 'border-transparent text-ink-muted hover:text-ink'
            }`
          }
        >
          {etiqueta}
        </NavLink>
      ))}
    </div>
  )
}
