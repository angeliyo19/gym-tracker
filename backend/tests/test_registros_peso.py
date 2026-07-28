import itertools

from fastapi.testclient import TestClient

USUARIO_EJEMPLO = {
    "nombre": "Angel",
    "edad": 25,
    "peso": 75.5,
    "altura": 1.78,
    "sexo": "masculino",
    "objetivo": "volumen",
}

_contador_email = itertools.count(1)


def _crear_usuario(client: TestClient) -> dict:
    email = f"angel{next(_contador_email)}@example.com"
    respuesta = client.post("/api/v1/usuarios/", json={**USUARIO_EJEMPLO, "email": email})
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_registro(client: TestClient, usuario_id: int, **overrides) -> dict:
    payload = {"usuario_id": usuario_id, "fecha": "2026-07-28", "peso": 76.2}
    payload.update(overrides)
    respuesta = client.post("/api/v1/registros-peso/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_registro_con_porcentaje_grasa(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/registros-peso/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "peso": 76.2,
            "porcentaje_grasa": 18.5,
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 76.2
    assert cuerpo["porcentaje_grasa"] == 18.5
    assert cuerpo["usuario_id"] == usuario["id"]


def test_crear_registro_sin_porcentaje_grasa(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/registros-peso/",
        json={"usuario_id": usuario["id"], "fecha": "2026-07-28", "peso": 76.2},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["porcentaje_grasa"] is None


def test_crear_registro_usuario_inexistente(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/registros-peso/",
        json={"usuario_id": 999999, "fecha": "2026-07-28", "peso": 76.2},
    )

    assert respuesta.status_code == 404


def test_listar_registros(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    _crear_registro(client, usuario["id"], peso=76.2)
    _crear_registro(client, usuario["id"], peso=75.8)

    respuesta = client.get("/api/v1/registros-peso/")

    assert respuesta.status_code == 200
    pesos = {registro["peso"] for registro in respuesta.json()}
    assert pesos == {76.2, 75.8}


def test_obtener_registro_por_id(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creado = _crear_registro(client, usuario["id"])

    respuesta = client.get(f"/api/v1/registros-peso/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_registro_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/registros-peso/999999")

    assert respuesta.status_code == 404


def test_actualizar_registro_parcial(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creado = _crear_registro(client, usuario["id"], peso=76.2)

    respuesta = client.patch(f"/api/v1/registros-peso/{creado['id']}", json={"peso": 75.5})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 75.5
    assert cuerpo["fecha"] == creado["fecha"]


def test_eliminar_registro(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creado = _crear_registro(client, usuario["id"])

    respuesta_delete = client.delete(f"/api/v1/registros-peso/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/registros-peso/{creado['id']}")
    assert respuesta_get.status_code == 404
