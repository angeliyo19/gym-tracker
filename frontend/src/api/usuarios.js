import { apiClient } from './client'

export function obtenerMiPerfil() {
  return apiClient.get('/api/v1/usuarios/me')
}
