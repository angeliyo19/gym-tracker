function IconoBarra(props) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M6 7v10M4 9v6M18 7v10M20 9v6M6 12h12" />
    </svg>
  )
}

export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-dashed border-border bg-surface/60 px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10 text-accent">
        {icon ?? <IconoBarra className="h-6 w-6" />}
      </div>
      <h3 className="mt-4 font-heading text-lg font-semibold text-ink">{title}</h3>
      {description && (
        <p className="mt-1 max-w-sm text-sm text-ink-muted">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}
