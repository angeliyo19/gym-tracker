# Gym Tracker — Contexto del proyecto

## Qué es esto
App web de seguimiento personal de gimnasio: entrenamientos, alimentación,
progresiones y estadísticas. Proyecto personal de aprendizaje, con visión de
escalar a análisis de técnica por vídeo/IA y predicción de progresión.

## Stack
- **Backend**: Python + FastAPI
- **Base de datos**: PostgreSQL (vía Docker en local)
- **ORM / migraciones**: SQLAlchemy + Alembic
- **Frontend**: React + Vite + Tailwind CSS
- **Control de versiones**: Git + GitHub (issues, ramas feature/*, PRs)

## Estructura de carpetas
```
gym-tracker/
├── backend/
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Schemas Pydantic (validación/serialización)
│   │   ├── routers/      # Endpoints FastAPI
│   │   ├── services/     # Lógica de negocio
│   │   ├── db.py         # Conexión a la base de datos
│   │   └── main.py       # Punto de entrada FastAPI
│   ├── alembic/          # Migraciones
│   ├── tests/
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/
        ├── pages/
        └── api/           # Llamadas al backend
```

## Modelo de datos (entidades principales)

Distinción clave: **Rutina** es una plantilla reutilizable (qué ejercicios, en
qué orden, con qué objetivo de series/reps). **SesionEntrenamiento** es una
ejecución real de esa rutina en una fecha concreta, con los pesos/reps reales
registrados en sus Series (que pueden diferir del objetivo de la rutina). Toda
sesión cuelga siempre de una rutina — si un día se quiere entrenar algo
distinto a lo habitual, se crea una rutina nueva (aunque sea de un solo uso) y
se inicia, no existen sesiones "sueltas" sin rutina.

- **Usuario**: nombre, email (único), edad, peso, altura, sexo, objetivo (volumen/definición/mantenimiento)
- **Ejercicio** (catálogo): nombre, tipo (compuesto/aislamiento)
- **GrupoMuscular** (catálogo): nombre (pecho, espalda, pierna, hombro, bíceps, tríceps...)
- **EjercicioGrupoMuscular** (tabla intermedia, relación muchos-a-muchos):
  ejercicio_id, grupo_muscular_id, es_principal (bool)
- **Rutina** (plantilla reutilizable): usuario_id, nombre
- **RutinaEjercicio** (qué ejercicios componen la rutina y su objetivo):
  rutina_id, ejercicio_id, orden, series_objetivo, repeticiones_objetivo
- **SesionEntrenamiento** (ejecución real de una rutina): usuario_id,
  rutina_id (obligatorio), fecha, notas
- **Serie** (lo realmente hecho en una sesión): sesion_id, ejercicio_id, peso,
  repeticiones, RPE/RIR
- **RegistroPeso**: usuario, fecha, peso, % grasa (opcional)

Alimentación — mismo patrón plantilla/ejecución que Rutina/Sesión:
- **Comida** (catálogo reutilizable, como Ejercicio): usuario_id, nombre/descripción, calorías (opcional)
- **PlanAlimentacion** (plantilla reutilizable, como Rutina): usuario_id, nombre
- **PlanDia** (qué comidas van en qué franja de qué día del ciclo, como RutinaEjercicio):
  plan_id, numero_dia, franja (desayuno/media_mañana/almuerzo/merienda/cena — valores
  fijos conocidos, validados en Pydantic, no en la BD), comida_id, orden. No todas las
  franjas son obligatorias cada día (un usuario puede no usar "media mañana")
- **RegistroAlimentacion** (registro real diario, como Serie): usuario_id, fecha,
  plan_dia_id (opcional, de qué día/franja del plan viene), comida_id (lo realmente
  comido, puede diferir de lo planeado), completada (bool), calorías (valor real)

- **RegistroEstadoAnimo**: usuario, fecha, valor (1-5), notas

Nota de diseño: qué grupos musculares trabaja una sesión NO se guarda como
campo fijo — se calcula dinámicamente a partir de los ejercicios de sus series,
para evitar que el dato quede desactualizado si cambian los ejercicios.

## Fases del proyecto
1. **MVP**: CRUD de usuarios, ejercicios, sesiones/series y alimentación + gráficas básicas de progresión
2. **Consolidación**: cálculo de 1RM estimado, volumen semanal, macros vs objetivo, etapas (volumen/definición)
3. **Predicción**: modelos de regresión sobre el histórico para predecir progresión de peso/reps.
   Fuentes de datos combinadas para el modelo (todas ya cruzables por `fecha` + `usuario_id`,
   no requieren tablas nuevas):
   - Progresión histórica de peso/repeticiones por ejercicio (Serie + SesionEntrenamiento.fecha)
   - Estado de ánimo del día de la sesión (RegistroEstadoAnimo), como proxy de disposición/motivación
   - Alimentación de una ventana de los últimos 1-2 días previos a la sesión (RegistroAlimentacion),
     no solo el mismo día — los depósitos de glucógeno se rellenan con la ingesta de días previos,
     no con la comida de esa misma mañana
   - Composición corporal reciente (RegistroPeso) y etapa del usuario (Usuario.objetivo:
     volumen/definición/mantenimiento), como contexto de fondo para no confundir una bajada de
     fuerza normal en definición con una señal de alarma
4. **Análisis de vídeo**: pose estimation (MediaPipe/OpenCV) para evaluar técnica

Nota de producto importante: **Entrenamiento y Alimentación son secciones
independientes** en la aplicación (navegación separada, no mezcladas en una
misma pantalla), aunque comparten el mismo Usuario. Los registros personales
(RegistroPeso, RegistroEstadoAnimo, RegistroAlimentacion) existen sobre todo
como **datos de entrada para la Fase 3 (predicción por IA)**: el objetivo final
es analizar la progresión real del usuario (peso, ánimo, alimentación,
rendimiento en el gym) para dar consejos útiles y guiarlo en su proceso, no
solo para mostrar gráficas históricas.

## Principios de diseño para que el proyecto escale bien
El proyecto se construye por fases, así que cada pieza debe montarse pensando
en que se ampliará después, sin necesidad de reescribirla:

- **Separación por capas** (routers → services → models): la lógica de negocio
  vive en `services/`, nunca directamente en los endpoints. Así, cuando en la
  Fase 3 añadamos predicción o en la Fase 4 análisis de vídeo, se integran como
  nuevos servicios sin tocar los endpoints existentes.
- **Modelos de datos abiertos a extensión**: por ejemplo, `Serie` debe permitir
  añadir campos opcionales en el futuro (ej. tempo, rango de movimiento) sin
  romper lo existente. Usar migraciones de Alembic para cada cambio, nunca
  editar tablas a mano.
- **Versionado de API desde el inicio**: todos los endpoints bajo `/api/v1/...`,
  para poder introducir `/api/v2/` en el futuro sin romper el frontend actual.
- **Configuración por variables de entorno** (`.env`): nunca hardcodear
  credenciales, URLs o claves — esto facilita mover el proyecto a otro entorno
  (ej. un servidor con GPU para la Fase 4 de análisis de vídeo).
- **Desacoplar el futuro análisis de vídeo/IA desde ya**: aunque no se
  implemente todavía, dejar pensado que el procesamiento pesado (vídeo, ML) se
  hará en un servicio/worker aparte (ej. cola de tareas), no dentro del mismo
  proceso que atiende peticiones HTTP normales.
- **Tests desde el principio**: cada endpoint nuevo con su test, para poder
  refactorizar con confianza cuando el proyecto crezca.

## Autenticación
- **Mecanismo**: JWT (Bearer token), vía `OAuth2PasswordBearer` de FastAPI.
  Sin refresh tokens por ahora — token de acceso único con expiración razonable.
- **Contraseñas**: hasheadas (nunca en texto plano) — campo `password_hash` en Usuario.
- **Frontend**: el token se guarda en `localStorage` (simple, sobrevive a recargar
  la página). Aceptado conscientemente el trade-off de seguridad frente a un
  cookie `httpOnly` — revisar si el proyecto llega a producción real con
  usuarios externos.
- **Endpoints existentes que reciben `usuario_id` como dato de entrada**
  (Rutina, SesionEntrenamiento, RegistroPeso, RegistroEstadoAnimo,
  RegistroAlimentacion, PlanAlimentacion) deben pasar a derivar el usuario del
  token autenticado (`Depends(get_current_user)`), no confiar en lo que envíe
  el cliente.

## Convenciones de código
- Python: seguir PEP8, type hints siempre, docstrings en funciones públicas
- Nombres de tablas/columnas en snake_case, en español (coherente con el dominio)
- Cada endpoint nuevo debe tener su test correspondiente en `tests/`
- Commits en español, formato: `tipo: descripción breve` (ej: `feat: añadir endpoint de registro de series`)

## Cómo trabajar conmigo (Claude Code) en este proyecto
- Pide tareas concretas y pequeñas (un endpoint, un modelo, un componente), no "hazme todo el módulo X"
- Antes de implementar algo nuevo y grande, pregúntame el enfoque primero si no está claro
- Explica siempre brevemente el porqué de decisiones no triviales
- No instales dependencias nuevas sin decírmelo primero