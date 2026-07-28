import { useEffect, useState } from 'react'
import { UsuariosPage } from './pages/UsuariosPage'
import { RutinasPage } from './pages/RutinasPage'
import { ThemeToggle } from './components/ThemeToggle'

const PAGINAS = {
  rutinas: { etiqueta: 'Rutinas', Componente: RutinasPage },
  usuarios: { etiqueta: 'Usuarios', Componente: UsuariosPage },
}

function App() {
  const [pagina, setPagina] = useState('rutinas')
  const [oscuro, setOscuro] = useState(false)
  const { Componente } = PAGINAS[pagina]

  useEffect(() => {
    document.documentElement.classList.toggle('dark', oscuro)
  }, [oscuro])

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-xl items-center justify-between px-8 py-4">
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent font-heading text-sm font-bold text-accent-foreground">
              G
            </span>
            <span className="font-heading text-base font-semibold text-ink">Gym Tracker</span>
          </div>

          <div className="flex items-center gap-3">
            <nav className="flex gap-1 rounded-full border border-border bg-surface p-1">
              {Object.entries(PAGINAS).map(([clave, { etiqueta }]) => (
                <button
                  key={clave}
                  type="button"
                  onClick={() => setPagina(clave)}
                  className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                    pagina === clave
                      ? 'bg-accent text-accent-foreground'
                      : 'text-ink-muted hover:text-ink'
                  }`}
                >
                  {etiqueta}
                </button>
              ))}
            </nav>
            <ThemeToggle oscuro={oscuro} onToggle={() => setOscuro((actual) => !actual)} />
          </div>
        </div>
      </header>
      <Componente />
    </div>
  )
}

export default App
