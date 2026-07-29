import { apiClient } from './client'

export function getGruposMusculares() {
  return apiClient.get('/api/v1/grupos-musculares/')
}

export function crearGrupoMuscular(datos) {
  return apiClient.post('/api/v1/grupos-musculares/', datos)
}

export function actualizarGrupoMuscular(id, datos) {
  return apiClient.patch(`/api/v1/grupos-musculares/${id}`, datos)
}

export function eliminarGrupoMuscular(id) {
  return apiClient.delete(`/api/v1/grupos-musculares/${id}`)
}
