import { apiClient } from './client'

export function obtenerMiPerfil() {
  return apiClient.get('/api/v1/usuarios/me')
}

export function actualizarMiPerfil(datos) {
  return apiClient.patch('/api/v1/usuarios/me', datos)
}
