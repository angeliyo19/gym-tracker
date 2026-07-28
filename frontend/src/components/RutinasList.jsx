import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { EmptyState } from './ui/EmptyState'
import { PageHeader } from './ui/PageHeader'

export function RutinasList({ rutinas, onSelect, onNew }) {
  return (
    <div>
      <PageHeader
        title="Rutinas"
        description="Plantillas reutilizables de entrenamiento."
        action={
          <Button variant="primary" onClick={onNew}>
            + Nueva rutina
          </Button>
        }
      />

      {rutinas.length === 0 && (
        <div className="mt-6">
          <EmptyState
            title="Todavía no hay rutinas"
            description="Crea tu primera rutina eligiendo ejercicios del catálogo."
            action={
              <Button variant="primary" onClick={onNew}>
                + Nueva rutina
              </Button>
            }
          />
        </div>
      )}

      {rutinas.length > 0 && (
        <Card className="mt-6 divide-y divide-border overflow-hidden">
          {rutinas.map((rutina) => (
            <button
              key={rutina.id}
              type="button"
              onClick={() => onSelect(rutina.id)}
              className="flex w-full items-center justify-between px-4 py-3.5 text-left transition-colors hover:bg-surface-hover"
            >
              <span className="font-medium text-ink">{rutina.nombre}</span>
              <span className="rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
                {rutina.ejercicios.length}{' '}
                {rutina.ejercicios.length === 1 ? 'ejercicio' : 'ejercicios'}
              </span>
            </button>
          ))}
        </Card>
      )}
    </div>
  )
}
