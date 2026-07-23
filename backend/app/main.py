from fastapi import FastAPI

app = FastAPI(title="Gym Tracker API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Comprueba que la API está viva."""
    return {"status": "ok"}
