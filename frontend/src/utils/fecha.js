// Evita new Date(iso) para no sufrir el desfase de un día que introduce
// interpretar una fecha "YYYY-MM-DD" en la zona horaria local.
export function formatearFecha(fechaIso) {
  const [anio, mes, dia] = fechaIso.split('-')
  return `${dia}/${mes}/${anio}`
}

// Duración entrenada real, a partir de hora_inicio/hora_fin (datetimes ISO
// con zona horaria). Devuelve null si la sesión no tiene ambos datos, ya sea
// porque no se ha empezado o porque todavía no se ha finalizado.
export function formatearDuracion(horaInicioIso, horaFinIso) {
  if (!horaInicioIso || !horaFinIso) return null

  const minutos = Math.round((new Date(horaFinIso) - new Date(horaInicioIso)) / 60000)
  if (minutos < 60) return `${minutos} min`

  const horas = Math.floor(minutos / 60)
  const minutosRestantes = minutos % 60
  return minutosRestantes > 0 ? `${horas} h ${minutosRestantes} min` : `${horas} h`
}
