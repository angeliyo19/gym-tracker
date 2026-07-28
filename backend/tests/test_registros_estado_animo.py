from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_registro(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"fecha": "2026-07-28", "valor": 4}
    payload.update(overrides)
    respuesta = client.post("/api/v1/registros-estado-animo/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_registro(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-estado-animo/",
        json={"fecha": "2026-07-28", "valor": 4, "notas": "Buen entreno hoy"},
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["valor"] == 4
    assert cuerpo["notas"] == "Buen entreno hoy"
    assert cuerpo["usuario_id"] == usuario["id"]


def test_crear_registro_sin_notas(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-estado-animo/",
        json={"fecha": "2026-07-28", "valor": 3},
        headers=headers,
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["notas"] is None


def test_crear_registro_valor_fuera_de_rango(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-estado-animo/",
        json={"fecha": "2026-07-28", "valor": 6},
        headers=headers,
    )

    assert respuesta.status_code == 422


def test_crear_registro_valor_cero(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-estado-animo/",
        json={"fecha": "2026-07-28", "valor": 0},
        headers=headers,
    )

    assert respuesta.status_code == 422


def test_crear_registro_sin_token(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/registros-estado-animo/", json={"fecha": "2026-07-28", "valor": 3}
    )

    assert respuesta.status_code == 401


def test_listar_registros(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    _crear_registro(client, headers, valor=4)
    _crear_registro(client, headers, valor=2)

    respuesta = client.get("/api/v1/registros-estado-animo/", headers=headers)

    assert respuesta.status_code == 200
    valores = {registro["valor"] for registro in respuesta.json()}
    assert valores == {4, 2}


def test_listar_registros_no_incluye_los_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    _crear_registro(client, headers_1, valor=4)
    _crear_registro(client, headers_2, valor=1)

    respuesta = client.get("/api/v1/registros-estado-animo/", headers=headers_1)

    assert respuesta.status_code == 200
    valores = {registro["valor"] for registro in respuesta.json()}
    assert valores == {4}


def test_obtener_registro_por_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers)

    respuesta = client.get(f"/api/v1/registros-estado-animo/{creado['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_registro_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers_1)

    respuesta = client.get(f"/api/v1/registros-estado-animo/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_registro_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/registros-estado-animo/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_registro_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers, valor=3)

    respuesta = client.patch(
        f"/api/v1/registros-estado-animo/{creado['id']}", json={"valor": 5}, headers=headers
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["valor"] == 5
    assert cuerpo["fecha"] == creado["fecha"]


def test_actualizar_registro_valor_fuera_de_rango(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers)

    respuesta = client.patch(
        f"/api/v1/registros-estado-animo/{creado['id']}", json={"valor": 10}, headers=headers
    )

    assert respuesta.status_code == 422


def test_eliminar_registro(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers)

    respuesta_delete = client.delete(
        f"/api/v1/registros-estado-animo/{creado['id']}", headers=headers
    )
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/registros-estado-animo/{creado['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_registro_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creado = _crear_registro(client, headers_1)

    respuesta = client.delete(
        f"/api/v1/registros-estado-animo/{creado['id']}", headers=headers_2
    )

    assert respuesta.status_code == 404
