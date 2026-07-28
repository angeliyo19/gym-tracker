import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { RutinasPage } from './pages/RutinasPage'
import { LoginPage } from './pages/LoginPage'
import { RegistroPage } from './pages/RegistroPage'
import { RutaProtegida } from './components/RutaProtegida'
import { ThemeToggle } from './components/ThemeToggle'
import { Button } from './components/ui/Button'
import { useAuth } from './context/AuthContext'

function App() {
  const [oscuro, setOscuro] = useState(false)
  const { usuario, logout } = useAuth()

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
            {usuario && (
              <Button variant="ghost" onClick={logout}>
                Cerrar sesión
              </Button>
            )}
            <ThemeToggle oscuro={oscuro} onToggle={() => setOscuro((actual) => !actual)} />
          </div>
        </div>
      </header>

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegistroPage />} />
        <Route
          path="/rutinas"
          element={
            <RutaProtegida>
              <RutinasPage />
            </RutaProtegida>
          }
        />
        <Route path="*" element={<Navigate to="/rutinas" replace />} />
      </Routes>
    </div>
  )
}

export default App
