import { apiClient } from './client'

export function getSesion(id) {
  return apiClient.get(`/api/v1/sesiones/${id}`)
}

export function finalizarSesion(id) {
  return apiClient.post(`/api/v1/sesiones/${id}/finalizar`)
}
