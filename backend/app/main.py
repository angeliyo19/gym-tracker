from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.comidas import router as comidas_router
from app.routers.ejercicios import router as ejercicios_router
from app.routers.grupos_musculares import router as grupos_musculares_router
from app.routers.planes_alimentacion import router as planes_alimentacion_router
from app.routers.registros_alimentacion import router as registros_alimentacion_router
from app.routers.registros_estado_animo import router as registros_estado_animo_router
from app.routers.registros_peso import router as registros_peso_router
from app.routers.rutinas import router as rutinas_router
from app.routers.series import router as series_router
from app.routers.usuarios import router as usuarios_router

app = FastAPI(title="Gym Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(usuarios_router, prefix="/api/v1")
app.include_router(ejercicios_router, prefix="/api/v1")
app.include_router(grupos_musculares_router, prefix="/api/v1")
app.include_router(rutinas_router, prefix="/api/v1")
app.include_router(series_router, prefix="/api/v1")
app.include_router(comidas_router, prefix="/api/v1")
app.include_router(planes_alimentacion_router, prefix="/api/v1")
app.include_router(registros_alimentacion_router, prefix="/api/v1")
app.include_router(registros_peso_router, prefix="/api/v1")
app.include_router(registros_estado_animo_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Comprueba que la API está viva."""
    return {"status": "ok"}
