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
- **Usuario**: edad, peso, altura, sexo, objetivo (volumen/definición/mantenimiento)
- **Ejercicio**: nombre, grupo muscular, tipo (compuesto/aislamiento)
- **SesionEntrenamiento**: fecha, usuario, notas
- **Serie**: sesion_id, ejercicio_id, peso, repeticiones, RPE/RIR
- **RegistroPeso**: usuario, fecha, peso, % grasa (opcional)
- **RegistroAlimentacion**: usuario, fecha, comida, proteína, carbs, grasas, calorías
- **RegistroEstadoAnimo**: usuario, fecha, valor (1-5), notas

## Fases del proyecto
1. **MVP**: CRUD de usuarios, ejercicios, sesiones/series y alimentación + gráficas básicas de progresión
2. **Consolidación**: cálculo de 1RM estimado, volumen semanal, macros vs objetivo, etapas (volumen/definición)
3. **Predicción**: modelos de regresión sobre el histórico para predecir progresión de peso/reps
4. **Análisis de vídeo**: pose estimation (MediaPipe/OpenCV) para evaluar técnica

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