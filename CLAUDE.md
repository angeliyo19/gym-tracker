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

Jerarquía central: Usuario → Sesión → Serie → Ejercicio (catálogo).
Una sesión NO tiene "ejercicios" directamente, tiene series realizadas; cada
serie referencia un ejercicio del catálogo. Así una sesión puede tener varias
series del mismo ejercicio con distinto peso/reps.

- **Usuario**: edad, peso, altura, sexo, objetivo (volumen/definición/mantenimiento)
- **Ejercicio** (catálogo): nombre, tipo (compuesto/aislamiento)
- **GrupoMuscular** (catálogo): nombre (pecho, espalda, pierna, hombro, bíceps, tríceps...)
- **EjercicioGrupoMuscular** (tabla intermedia, relación muchos-a-muchos):
  ejercicio_id, grupo_muscular_id, es_principal (bool, para distinguir músculo
  principal vs secundario de ese ejercicio)
- **SesionEntrenamiento**: fecha, usuario, notas
- **Serie**: sesion_id, ejercicio_id, peso, repeticiones, RPE/RIR
- **RegistroPeso**: usuario, fecha, peso, % grasa (opcional)
- **RegistroAlimentacion**: usuario, fecha, comida, proteína, carbs, grasas, calorías
- **RegistroEstadoAnimo**: usuario, fecha, valor (1-5), notas

Nota de diseño: qué grupos musculares trabaja una sesión NO se guarda como
campo fijo — se calcula dinámicamente a partir de los ejercicios de sus series,
para evitar que el dato quede desactualizado si cambian los ejercicios.

## Fases del proyecto
1. **MVP**: CRUD de usuarios, ejercicios, sesiones/series y alimentación + gráficas básicas de progresión
2. **Consolidación**: cálculo de 1RM estimado, volumen semanal, macros vs objetivo, etapas (volumen/definición)
3. **Predicción**: modelos de regresión sobre el histórico para predecir progresión de peso/reps
4. **Análisis de vídeo**: pose estimation (MediaPipe/OpenCV) para evaluar técnica

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