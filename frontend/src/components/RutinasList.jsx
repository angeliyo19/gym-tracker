export function RutinasList({ rutinas, onSelect, onNew }) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Rutinas</h1>
        <button
          type="button"
          onClick={onNew}
          className="rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-700"
        >
          Nueva rutina
        </button>
      </div>

      {rutinas.length === 0 && <p className="mt-6 text-gray-500">No hay rutinas todavía.</p>}

      {rutinas.length > 0 && (
        <ul className="mt-6 divide-y divide-gray-200 rounded-md border border-gray-200">
          {rutinas.map((rutina) => (
            <li key={rutina.id}>
              <button
                type="button"
                onClick={() => onSelect(rutina.id)}
                className="flex w-full items-center justify-between p-3 text-left hover:bg-gray-50"
              >
                <span className="font-medium text-gray-900">{rutina.nombre}</span>
                <span className="text-sm text-gray-500">
                  {rutina.ejercicios.length}{' '}
                  {rutina.ejercicios.length === 1 ? 'ejercicio' : 'ejercicios'}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
