import { apiClient } from './client'

export function getEjercicios() {
  return apiClient.get('/api/v1/ejercicios/')
}
