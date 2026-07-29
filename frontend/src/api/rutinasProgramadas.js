import { apiClient } from './client'

export function getRutinasProgramadas() {
  return apiClient.get('/api/v1/rutinas-programadas/')
}

export function crearRutinaProgramada(datos) {
  return apiClient.post('/api/v1/rutinas-programadas/', datos)
}

export function actualizarRutinaProgramada(id, datos) {
  return apiClient.patch(`/api/v1/rutinas-programadas/${id}`, datos)
}

export function eliminarRutinaProgramada(id) {
  return apiClient.delete(`/api/v1/rutinas-programadas/${id}`)
}
