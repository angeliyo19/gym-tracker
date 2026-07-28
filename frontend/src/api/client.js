const BASE_URL = import.meta.env.VITE_API_BASE_URL
const CLAVE_TOKEN = 'token'

let manejadorNoAutorizado = null

export function registrarManejadorNoAutorizado(fn) {
  manejadorNoAutorizado = fn
}

async function request(path, options = {}) {
  const token = localStorage.getItem(CLAVE_TOKEN)
  const { headers: headersPersonalizados, ...resto } = options

  const respuesta = await fetch(`${BASE_URL}${path}`, {
    ...resto,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headersPersonalizados,
    },
  })

  // Solo si había un token de por medio: un 401 sin token (ej. login con
  // contraseña incorrecta) es simplemente una credencial inválida, no una
  // sesión caducada.
  if (respuesta.status === 401 && token) {
    manejadorNoAutorizado?.()
  }

  if (!respuesta.ok) {
    throw new Error(`Error ${respuesta.status} al llamar a ${path}`)
  }

  if (respuesta.status === 204) {
    return null
  }

  return respuesta.json()
}

export const apiClient = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  patch: (path, body) => request(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: 'DELETE' }),
  postForm: (path, datosFormulario) =>
    request(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(datosFormulario).toString(),
    }),
}
