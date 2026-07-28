from fastapi import FastAPI

from app.routers.ejercicios import router as ejercicios_router
from app.routers.grupos_musculares import router as grupos_musculares_router
from app.routers.rutinas import router as rutinas_router
from app.routers.series import router as series_router
from app.routers.usuarios import router as usuarios_router

app = FastAPI(title="Gym Tracker API")

app.include_router(usuarios_router, prefix="/api/v1")
app.include_router(ejercicios_router, prefix="/api/v1")
app.include_router(grupos_musculares_router, prefix="/api/v1")
app.include_router(rutinas_router, prefix="/api/v1")
app.include_router(series_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Comprueba que la API está viva."""
    return {"status": "ok"}
