import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { InicioPage } from './pages/InicioPage'
import { RutinasPage } from './pages/RutinasPage'
import { SesionEnVivoPage } from './pages/SesionEnVivoPage'
import { AlimentacionPage } from './pages/AlimentacionPage'
import { LoginPage } from './pages/LoginPage'
import { RegistroPage } from './pages/RegistroPage'
import { RutaProtegida } from './components/RutaProtegida'
import { LayoutPrincipal } from './components/LayoutPrincipal'
import { ThemeToggle } from './components/ThemeToggle'

function App() {
  const [oscuro, setOscuro] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', oscuro)
  }, [oscuro])

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-8 py-4">
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent font-heading text-sm font-bold text-accent-foreground">
              G
            </span>
            <span className="font-heading text-base font-semibold text-ink">Gym Tracker</span>
          </div>
          <ThemeToggle oscuro={oscuro} onToggle={() => setOscuro((actual) => !actual)} />
        </div>
      </header>

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegistroPage />} />

        <Route element={<RutaProtegida />}>
          <Route element={<LayoutPrincipal />}>
            <Route path="/" element={<InicioPage />} />
            <Route path="/entrenamiento/rutinas" element={<RutinasPage />} />
            <Route path="/entrenamiento/sesiones/:id" element={<SesionEnVivoPage />} />
            <Route path="/alimentacion" element={<AlimentacionPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
