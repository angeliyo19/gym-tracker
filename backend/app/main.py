from fastapi import FastAPI

from app.routers.usuarios import router as usuarios_router

app = FastAPI(title="Gym Tracker API")

app.include_router(usuarios_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Comprueba que la API está viva."""
    return {"status": "ok"}
