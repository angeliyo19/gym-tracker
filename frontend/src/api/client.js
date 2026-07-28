const BASE_URL = import.meta.env.VITE_API_BASE_URL

async function request(path, options = {}) {
  const respuesta = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

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
}
