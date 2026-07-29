import { apiClient } from './client'

export function crearSerie(sesionId, datos) {
  return apiClient.post(`/api/v1/sesiones/${sesionId}/series/`, datos)
}

export function eliminarSerie(sesionId, serieId) {
  return apiClient.delete(`/api/v1/sesiones/${sesionId}/series/${serieId}`)
}
