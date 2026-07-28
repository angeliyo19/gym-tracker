import { apiClient } from './client'

export function registrarUsuario(datos) {
  return apiClient.post('/api/v1/auth/registro', datos)
}

export function iniciarSesion(email, password) {
  return apiClient.postForm('/api/v1/auth/login', { username: email, password })
}
