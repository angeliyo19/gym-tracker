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
