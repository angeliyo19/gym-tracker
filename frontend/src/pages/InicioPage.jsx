import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Card } from '../components/ui/Card'

const SECCIONES = [
  {
    to: '/entrenamiento/rutinas',
    titulo: 'Entrenamiento',
    descripcion: 'Rutinas, sesiones y progresión de tus levantamientos.',
  },
  {
    to: '/alimentacion',
    titulo: 'Alimentación',
    descripcion: 'Planes de comidas y registro diario.',
  },
]

export function InicioPage() {
  const { usuario } = useAuth()

  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      <h1 className="font-heading text-2xl font-semibold text-ink">Hola, {usuario.nombre}</h1>
      <p className="mt-1 text-sm text-ink-muted">¿Qué quieres hacer hoy?</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {SECCIONES.map(({ to, titulo, descripcion }) => (
          <Link key={to} to={to} className="block">
            <Card className="h-full p-5 transition-colors hover:bg-surface-hover">
              <h2 className="font-heading text-lg font-semibold text-ink">{titulo}</h2>
              <p className="mt-1 text-sm text-ink-muted">{descripcion}</p>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  )
}
