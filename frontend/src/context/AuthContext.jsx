import { createContext, useContext, useEffect, useState } from 'react'
import { iniciarSesion, registrarUsuario } from '../api/auth'
import { registrarManejadorNoAutorizado } from '../api/client'
import { obtenerMiPerfil } from '../api/usuarios'

const CLAVE_TOKEN = 'token'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  function cerrarSesion() {
    localStorage.removeItem(CLAVE_TOKEN)
    setUsuario(null)
  }

  useEffect(() => {
    registrarManejadorNoAutorizado(cerrarSesion)
  }, [])

  useEffect(() => {
    if (!localStorage.getItem(CLAVE_TOKEN)) {
      setCargando(false)
      return
    }
    obtenerMiPerfil()
      .then(setUsuario)
      .catch(cerrarSesion)
      .finally(() => setCargando(false))
    // Solo debe ejecutarse una vez al montar, para validar una sesión ya guardada.
    // eslint-disable-next-line
  }, [])

  async function login(email, password) {
    const { access_token: token } = await iniciarSesion(email, password)
    localStorage.setItem(CLAVE_TOKEN, token)
    const perfil = await obtenerMiPerfil()
    setUsuario(perfil)
  }

  async function registro(datosUsuario) {
    await registrarUsuario(datosUsuario)
    await login(datosUsuario.email, datosUsuario.password)
  }

  return (
    <AuthContext.Provider
      value={{
        usuario,
        cargando,
        login,
        registro,
        logout: cerrarSesion,
        actualizarUsuario: setUsuario,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const contexto = useContext(AuthContext)
  if (!contexto) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider')
  }
  return contexto
}
