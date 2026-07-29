import { apiClient } from './client'

export function getRutinas() {
  return apiClient.get('/api/v1/rutinas/')
}

export function getRutina(id) {
  return apiClient.get(`/api/v1/rutinas/${id}`)
}

export function createRutina(rutina) {
  return apiClient.post('/api/v1/rutinas/', rutina)
}

export function updateRutina(id, datos) {
  return apiClient.patch(`/api/v1/rutinas/${id}`, datos)
}

export function iniciarRutina(id) {
  return apiClient.post(`/api/v1/rutinas/${id}/iniciar`)
}
