import { apiClient } from './client'

export function crearSerie(sesionId, datos) {
  return apiClient.post(`/api/v1/sesiones/${sesionId}/series/`, datos)
}
