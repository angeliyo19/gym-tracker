import { useState } from 'react'
import { UsuariosPage } from './pages/UsuariosPage'
import { RutinasPage } from './pages/RutinasPage'

const PAGINAS = {
  usuarios: { etiqueta: 'Usuarios', Componente: UsuariosPage },
  rutinas: { etiqueta: 'Rutinas', Componente: RutinasPage },
}

function App() {
  const [pagina, setPagina] = useState('rutinas')
  const { Componente } = PAGINAS[pagina]

  return (
    <div>
      <nav className="flex gap-4 border-b border-gray-200 px-8 py-3">
        {Object.entries(PAGINAS).map(([clave, { etiqueta }]) => (
          <button
            key={clave}
            type="button"
            onClick={() => setPagina(clave)}
            className={`text-sm font-medium ${
              pagina === clave ? 'text-gray-900' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            {etiqueta}
          </button>
        ))}
      </nav>
      <Componente />
    </div>
  )
}

export default App
