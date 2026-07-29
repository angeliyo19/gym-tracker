import { useEffect } from 'react'
import { Card } from './Card'

export function Modal({ title, onClose, children }) {
  useEffect(() => {
    function manejarTecla(evento) {
      if (evento.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', manejarTecla)
    return () => document.removeEventListener('keydown', manejarTecla)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <Card
        className="w-full max-w-sm p-5"
        onClick={(evento) => evento.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-heading text-lg font-semibold text-ink">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="text-ink-muted hover:text-ink"
          >
            ✕
          </button>
        </div>
        <div className="mt-4">{children}</div>
      </Card>
    </div>
  )
}
