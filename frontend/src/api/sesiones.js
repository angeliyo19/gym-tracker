import { apiClient } from './client'

export function getSesiones(rutinaId) {
  const query = rutinaId ? `?rutina_id=${rutinaId}` : ''
  return apiClient.get(`/api/v1/sesiones/${query}`)
}

export function getSesion(id) {
  return apiClient.get(`/api/v1/sesiones/${id}`)
}

export function actualizarSesion(id, datos) {
  return apiClient.patch(`/api/v1/sesiones/${id}`, datos)
}

export function finalizarSesion(id) {
  return apiClient.post(`/api/v1/sesiones/${id}/finalizar`)
}
