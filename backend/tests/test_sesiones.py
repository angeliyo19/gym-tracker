from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_rutina(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"nombre": "Push day", "ejercicios": []}
    payload.update(overrides)
    respuesta = client.post("/api/v1/rutinas/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def _iniciar_rutina(client: TestClient, rutina_id: int, headers: dict) -> dict:
    respuesta = client.post(f"/api/v1/rutinas/{rutina_id}/iniciar", headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_finalizar_sesion(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    assert sesion["completada"] is False

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True


def test_finalizar_sesion_es_idempotente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    primera = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)
    segunda = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    assert primera.status_code == 200
    assert segunda.status_code == 200
    assert segunda.json()["completada"] is True


def test_finalizar_sesion_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    sesion = _iniciar_rutina(client, rutina["id"], headers_1)

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers_2)

    assert respuesta.status_code == 404


def test_finalizar_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post("/api/v1/sesiones/999999/finalizar", headers=headers)

    assert respuesta.status_code == 404


def test_finalizar_sesion_sin_token(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar")

    assert respuesta.status_code == 401
