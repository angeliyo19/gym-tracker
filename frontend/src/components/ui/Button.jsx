const BASE =
  'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 ' +
  'focus-visible:ring-offset-canvas disabled:opacity-50 disabled:pointer-events-none'

const VARIANTES = {
  primary: 'bg-accent text-accent-foreground hover:bg-accent-hover px-4 py-2 text-sm shadow-sm',
  secondary:
    'bg-surface text-ink border border-border hover:bg-surface-hover px-4 py-2 text-sm',
  ghost: 'text-ink-muted hover:text-ink hover:bg-surface-hover px-3 py-1.5 text-sm',
  danger: 'text-red-500 hover:bg-red-500/10 px-3 py-1.5 text-sm',
}

export function Button({ variant = 'primary', className = '', ...props }) {
  return <button className={`${BASE} ${VARIANTES[variant]} ${className}`} {...props} />
}
