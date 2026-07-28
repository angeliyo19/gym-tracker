import { EmptyState } from '../components/ui/EmptyState'

export function AlimentacionPage() {
  return (
    <main className="mx-auto max-w-xl px-8 py-10">
      <h1 className="font-heading text-2xl font-semibold text-ink">Alimentación</h1>
      <p className="mt-1 text-sm text-ink-muted">Planes de comidas y registro diario.</p>

      <div className="mt-8">
        <EmptyState
          title="Próximamente"
          description="Esta sección todavía se está construyendo. Vuelve pronto."
        />
      </div>
    </main>
  )
}
