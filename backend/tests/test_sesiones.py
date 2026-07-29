from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_ejercicio(client: TestClient, nombre: str = "Press banca") -> dict:
    respuesta = client.post(
        "/api/v1/ejercicios/", json={"nombre": nombre, "tipo": "compuesto", "grupos_musculares": []}
    )
    assert respuesta.status_code == 201
    return respuesta.json()


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


def test_obtener_sesion(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8}
        ],
    )
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == sesion["id"]
    assert cuerpo["usuario_id"] == usuario["id"]
    assert cuerpo["completada"] is False
    assert cuerpo["rutina"]["id"] == rutina["id"]
    assert cuerpo["rutina"]["nombre"] == "Push day"
    assert len(cuerpo["rutina"]["ejercicios"]) == 1
    assert cuerpo["rutina"]["ejercicios"][0]["ejercicio"]["nombre"] == "Press banca"
    assert cuerpo["ultimas_series"] == []


def test_obtener_sesion_incluye_ultima_serie_por_ejercicio(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8}
        ],
    )
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": press["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )

    siguiente_sesion = _iniciar_rutina(client, rutina["id"], headers)
    respuesta = client.get(f"/api/v1/sesiones/{siguiente_sesion['id']}", headers=headers)

    assert respuesta.status_code == 200
    referencia = respuesta.json()["ultimas_series"][0]
    assert referencia["ejercicio_id"] == press["id"]
    assert referencia["peso"] == 80.0
    assert referencia["repeticiones"] == 8


def test_obtener_sesion_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    sesion = _iniciar_rutina(client, rutina["id"], headers_1)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/sesiones/999999", headers=headers)

    assert respuesta.status_code == 404


def test_obtener_sesion_sin_token(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}")

    assert respuesta.status_code == 401


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
