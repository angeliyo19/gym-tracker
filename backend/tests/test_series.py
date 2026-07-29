from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_ejercicio(client: TestClient, nombre: str = "Press banca") -> dict:
    respuesta = client.post(
        "/api/v1/ejercicios/", json={"nombre": nombre, "tipo": "compuesto", "grupos_musculares": []}
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_sesion(client: TestClient) -> tuple[dict, dict]:
    _, headers = crear_usuario_autenticado(client)
    ejercicio_de_la_rutina = _crear_ejercicio(client, "Sentadilla")
    respuesta_rutina = client.post(
        "/api/v1/rutinas/",
        json={
            "nombre": "Push day",
            "ejercicios": [
                {
                    "ejercicio_id": ejercicio_de_la_rutina["id"],
                    "orden": 1,
                    "series_objetivo": 3,
                    "repeticiones_objetivo": 10,
                }
            ],
        },
        headers=headers,
    )
    assert respuesta_rutina.status_code == 201
    rutina = respuesta_rutina.json()

    respuesta_sesion = client.post(f"/api/v1/rutinas/{rutina['id']}/iniciar", headers=headers)
    assert respuesta_sesion.status_code == 201
    return respuesta_sesion.json(), headers


def _crear_serie(
    client: TestClient, sesion_id: int, ejercicio_id: int, headers: dict, **overrides
) -> dict:
    payload = {"ejercicio_id": ejercicio_id, "peso": 80.0, "repeticiones": 8, "rpe": 8.5, "rir": 1.0}
    payload.update(overrides)
    respuesta = client.post(
        f"/api/v1/sesiones/{sesion_id}/series/", json=payload, headers=headers
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_serie(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)

    respuesta = client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8, "rpe": 8.5, "rir": 1.0},
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["sesion_id"] == sesion["id"]
    assert cuerpo["ejercicio_id"] == ejercicio["id"]
    assert cuerpo["peso"] == 80.0
    assert cuerpo["repeticiones"] == 8


def test_crear_serie_fija_hora_inicio_de_la_sesion(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    assert sesion["hora_inicio"] is None

    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers)
    cuerpo = respuesta.json()
    assert cuerpo["hora_inicio"] is not None
    assert cuerpo["hora_fin"] is None


def test_crear_segunda_serie_no_sobrescribe_hora_inicio(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)

    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )
    hora_inicio_tras_primera = client.get(
        f"/api/v1/sesiones/{sesion['id']}", headers=headers
    ).json()["hora_inicio"]

    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 82.5, "repeticiones": 6},
        headers=headers,
    )
    hora_inicio_tras_segunda = client.get(
        f"/api/v1/sesiones/{sesion['id']}", headers=headers
    ).json()["hora_inicio"]

    assert hora_inicio_tras_primera == hora_inicio_tras_segunda


def test_crear_serie_sin_token(client: TestClient) -> None:
    sesion, _ = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)

    respuesta = client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8},
    )

    assert respuesta.status_code == 401


def test_crear_serie_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    ejercicio = _crear_ejercicio(client)

    respuesta = client.post(
        "/api/v1/sesiones/999999/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_crear_serie_sesion_de_otro_usuario(client: TestClient) -> None:
    sesion, _ = _crear_sesion(client)
    _, headers_2 = crear_usuario_autenticado(client)
    ejercicio = _crear_ejercicio(client)

    respuesta = client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers_2,
    )

    assert respuesta.status_code == 404


def test_crear_serie_ejercicio_inexistente(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)

    respuesta = client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": 999999, "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_listar_series(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    _crear_serie(client, sesion["id"], ejercicio["id"], headers, peso=80.0)
    _crear_serie(client, sesion["id"], ejercicio["id"], headers, peso=85.0)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}/series/", headers=headers)

    assert respuesta.status_code == 200
    pesos = {serie["peso"] for serie in respuesta.json()}
    assert pesos == {80.0, 85.0}


def test_listar_series_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/sesiones/999999/series/", headers=headers)

    assert respuesta.status_code == 404


def test_listar_series_sesion_de_otro_usuario(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    _crear_serie(client, sesion["id"], ejercicio["id"], headers)
    _, headers_2 = crear_usuario_autenticado(client)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}/series/", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_serie_por_id(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"], headers)

    respuesta = client.get(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}", headers=headers
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_serie_inexistente(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}/series/999999", headers=headers)

    assert respuesta.status_code == 404


def test_obtener_serie_de_otra_sesion(client: TestClient) -> None:
    sesion_1, headers_1 = _crear_sesion(client)
    sesion_2, headers_2 = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion_1["id"], ejercicio["id"], headers_1)

    respuesta = client.get(
        f"/api/v1/sesiones/{sesion_2['id']}/series/{creada['id']}", headers=headers_2
    )

    assert respuesta.status_code == 404


def test_actualizar_serie_parcial(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"], headers, peso=80.0)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}",
        json={"peso": 85.0},
        headers=headers,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 85.0
    assert cuerpo["repeticiones"] == creada["repeticiones"]


def test_actualizar_serie_ejercicio_inexistente(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"], headers)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}",
        json={"ejercicio_id": 999999},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_eliminar_serie(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"], headers)

    respuesta_delete = client.delete(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}", headers=headers
    )
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}", headers=headers
    )
    assert respuesta_get.status_code == 404


def test_eliminar_serie_de_otra_sesion(client: TestClient) -> None:
    sesion, headers = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"], headers)
    _, headers_2 = crear_usuario_autenticado(client)

    respuesta = client.delete(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}", headers=headers_2
    )

    assert respuesta.status_code == 404
