// Evita new Date(iso) para no sufrir el desfase de un día que introduce
// interpretar una fecha "YYYY-MM-DD" en la zona horaria local.
export function formatearFecha(fechaIso) {
  const [anio, mes, dia] = fechaIso.split('-')
  return `${dia}/${mes}/${anio}`
}
