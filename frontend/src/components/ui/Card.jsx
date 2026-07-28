export function Card({ className = '', children, ...props }) {
  return (
    <div
      className={`rounded-2xl border border-border bg-surface shadow-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
