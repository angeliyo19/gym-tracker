from fastapi.testclient import TestClient

USUARIO_EJEMPLO = {
    "nombre": "Angel",
    "email": "angel@example.com",
    "edad": 25,
    "peso": 75.5,
    "altura": 1.78,
    "sexo": "masculino",
    "objetivo": "volumen",
}


def _crear_usuario(client: TestClient, **overrides) -> dict:
    payload = {**USUARIO_EJEMPLO, **overrides}
    respuesta = client.post("/api/v1/usuarios/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_usuario(client: TestClient) -> None:
    respuesta = client.post("/api/v1/usuarios/", json=USUARIO_EJEMPLO)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] is not None
    assert cuerpo["nombre"] == USUARIO_EJEMPLO["nombre"]
    assert cuerpo["email"] == USUARIO_EJEMPLO["email"]


def test_crear_usuario_email_duplicado(client: TestClient) -> None:
    _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/usuarios/",
        json={**USUARIO_EJEMPLO, "nombre": "Otro"},
    )

    assert respuesta.status_code == 409


def test_listar_usuarios(client: TestClient) -> None:
    _crear_usuario(client, email="uno@example.com")
    _crear_usuario(client, email="dos@example.com")

    respuesta = client.get("/api/v1/usuarios/")

    assert respuesta.status_code == 200
    emails = {usuario["email"] for usuario in respuesta.json()}
    assert emails == {"uno@example.com", "dos@example.com"}


def test_obtener_usuario_por_id(client: TestClient) -> None:
    creado = _crear_usuario(client)

    respuesta = client.get(f"/api/v1/usuarios/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_usuario_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/usuarios/999999")

    assert respuesta.status_code == 404


def test_actualizar_usuario_parcial(client: TestClient) -> None:
    creado = _crear_usuario(client)

    respuesta = client.patch(f"/api/v1/usuarios/{creado['id']}", json={"peso": 80})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 80
    assert cuerpo["nombre"] == creado["nombre"]
    assert cuerpo["email"] == creado["email"]


def test_eliminar_usuario(client: TestClient) -> None:
    creado = _crear_usuario(client)

    respuesta_delete = client.delete(f"/api/v1/usuarios/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/usuarios/{creado['id']}")
    assert respuesta_get.status_code == 404
