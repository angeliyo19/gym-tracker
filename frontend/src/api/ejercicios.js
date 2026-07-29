import { apiClient } from './client'

export function getEjercicios() {
  return apiClient.get('/api/v1/ejercicios/')
}

export function crearEjercicio(datos) {
  return apiClient.post('/api/v1/ejercicios/', datos)
}

export function actualizarEjercicio(id, datos) {
  return apiClient.patch(`/api/v1/ejercicios/${id}`, datos)
}

export function eliminarEjercicio(id) {
  return apiClient.delete(`/api/v1/ejercicios/${id}`)
}
