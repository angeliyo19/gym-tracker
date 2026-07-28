import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Base

PASSWORD_POR_DEFECTO = "clave-super-segura-123"

_contador_email = itertools.count(1)

engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session", autouse=True)
def preparar_esquema_test():
    """Crea el esquema completo en la BD de test antes de la sesión y lo elimina al final."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def limpiar_base_datos():
    """Deja la BD de test vacía tras cada test para que no se interfieran entre sí."""
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def registrar_usuario(client: TestClient, **overrides) -> dict:
    """Registra un usuario nuevo vía /auth/registro y devuelve el usuario creado."""
    payload = {
        "nombre": "Angel",
        "email": f"user{next(_contador_email)}@example.com",
        "edad": 25,
        "peso": 75.5,
        "altura": 1.78,
        "sexo": "masculino",
        "objetivo": "volumen",
        "password": PASSWORD_POR_DEFECTO,
    }
    payload.update(overrides)
    respuesta = client.post("/api/v1/auth/registro", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def obtener_token(client: TestClient, email: str, password: str = PASSWORD_POR_DEFECTO) -> str:
    """Inicia sesión vía /auth/login (form-encoded, como espera OAuth2PasswordRequestForm)."""
    respuesta = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    assert respuesta.status_code == 200
    return respuesta.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def crear_usuario_autenticado(client: TestClient, **overrides) -> tuple[dict, dict]:
    """Registra un usuario y devuelve (usuario, headers) listos para usar en peticiones."""
    usuario = registrar_usuario(client, **overrides)
    token = obtener_token(client, usuario["email"])
    return usuario, auth_headers(token)
