export function PageHeader({ title, description, action }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div>
        <h1 className="font-heading text-2xl font-semibold tracking-tight text-ink">{title}</h1>
        {description && <p className="mt-1 text-sm text-ink-muted">{description}</p>}
      </div>
      {action}
    </div>
  )
}
