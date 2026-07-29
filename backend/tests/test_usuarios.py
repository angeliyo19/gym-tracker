from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def test_obtener_mi_perfil(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/usuarios/me", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == usuario


def test_obtener_mi_perfil_sin_token(client: TestClient) -> None:
    respuesta = client.get("/api/v1/usuarios/me")

    assert respuesta.status_code == 401


def test_actualizar_mi_perfil_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.patch("/api/v1/usuarios/me", json={"peso": 80}, headers=headers)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 80


def test_nuevo_usuario_tiene_rol_usuario_por_defecto(client: TestClient) -> None:
    usuario, _ = crear_usuario_autenticado(client)

    assert usuario["rol"] == "usuario"


def test_actualizar_mi_perfil_no_permite_cambiar_rol(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.patch("/api/v1/usuarios/me", json={"rol": "admin"}, headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "usuario"


def test_eliminar_mi_perfil(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta_delete = client.delete("/api/v1/usuarios/me", headers=headers)
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get("/api/v1/usuarios/me", headers=headers)
    assert respuesta_get.status_code == 401
