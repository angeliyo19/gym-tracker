import { apiClient } from './client'

export function getUsuarios() {
  return apiClient.get('/api/v1/usuarios/')
}
