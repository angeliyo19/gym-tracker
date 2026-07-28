from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_registro(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"fecha": "2026-07-28", "peso": 76.2}
    payload.update(overrides)
    respuesta = client.post("/api/v1/registros-peso/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_registro_con_porcentaje_grasa(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-peso/",
        json={"fecha": "2026-07-28", "peso": 76.2, "porcentaje_grasa": 18.5},
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 76.2
    assert cuerpo["porcentaje_grasa"] == 18.5
    assert cuerpo["usuario_id"] == usuario["id"]


def test_crear_registro_sin_porcentaje_grasa(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-peso/",
        json={"fecha": "2026-07-28", "peso": 76.2},
        headers=headers,
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["porcentaje_grasa"] is None


def test_crear_registro_sin_token(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/registros-peso/", json={"fecha": "2026-07-28", "peso": 76.2}
    )

    assert respuesta.status_code == 401


def test_listar_registros(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    _crear_registro(client, headers, peso=76.2)
    _crear_registro(client, headers, peso=75.8)

    respuesta = client.get("/api/v1/registros-peso/", headers=headers)

    assert respuesta.status_code == 200
    pesos = {registro["peso"] for registro in respuesta.json()}
    assert pesos == {76.2, 75.8}


def test_listar_registros_no_incluye_los_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    _crear_registro(client, headers_1, peso=76.2)
    _crear_registro(client, headers_2, peso=90.0)

    respuesta = client.get("/api/v1/registros-peso/", headers=headers_1)

    assert respuesta.status_code == 200
    pesos = {registro["peso"] for registro in respuesta.json()}
    assert pesos == {76.2}


def test_obtener_registro_por_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers)

    respuesta = client.get(f"/api/v1/registros-peso/{creado['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_registro_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers_1)

    respuesta = client.get(f"/api/v1/registros-peso/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_registro_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/registros-peso/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_registro_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers, peso=76.2)

    respuesta = client.patch(
        f"/api/v1/registros-peso/{creado['id']}", json={"peso": 75.5}, headers=headers
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 75.5
    assert cuerpo["fecha"] == creado["fecha"]


def test_eliminar_registro(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers)

    respuesta_delete = client.delete(f"/api/v1/registros-peso/{creado['id']}", headers=headers)
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/registros-peso/{creado['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_registro_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers_1)

    respuesta = client.delete(f"/api/v1/registros-peso/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404
