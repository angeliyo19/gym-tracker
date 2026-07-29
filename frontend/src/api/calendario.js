import { apiClient } from './client'

export function getCalendario(desde, hasta) {
  return apiClient.get(`/api/v1/calendario?desde=${desde}&hasta=${hasta}`)
}
