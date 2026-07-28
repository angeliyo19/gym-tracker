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


def _crear_ejercicio(client: TestClient, nombre: str = "Press banca") -> dict:
    respuesta = client.post(
        "/api/v1/ejercicios/", json={"nombre": nombre, "tipo": "compuesto", "grupos_musculares": []}
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_sesion(client: TestClient) -> dict:
    usuario = _crear_usuario(client)
    respuesta_rutina = client.post(
        "/api/v1/rutinas/", json={"nombre": "Push day", "usuario_id": usuario["id"], "ejercicios": []}
    )
    assert respuesta_rutina.status_code == 201
    rutina = respuesta_rutina.json()

    respuesta_sesion = client.post(f"/api/v1/rutinas/{rutina['id']}/iniciar")
    assert respuesta_sesion.status_code == 201
    return respuesta_sesion.json()


def _crear_serie(client: TestClient, sesion_id: int, ejercicio_id: int, **overrides) -> dict:
    payload = {"ejercicio_id": ejercicio_id, "peso": 80.0, "repeticiones": 8, "rpe": 8.5, "rir": 1.0}
    payload.update(overrides)
    respuesta = client.post(f"/api/v1/sesiones/{sesion_id}/series/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_serie(client: TestClient) -> None:
    sesion = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)

    respuesta = client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8, "rpe": 8.5, "rir": 1.0},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["sesion_id"] == sesion["id"]
    assert cuerpo["ejercicio_id"] == ejercicio["id"]
    assert cuerpo["peso"] == 80.0
    assert cuerpo["repeticiones"] == 8


def test_crear_serie_sesion_inexistente(client: TestClient) -> None:
    ejercicio = _crear_ejercicio(client)

    respuesta = client.post(
        "/api/v1/sesiones/999999/series/",
        json={"ejercicio_id": ejercicio["id"], "peso": 80.0, "repeticiones": 8},
    )

    assert respuesta.status_code == 404


def test_crear_serie_ejercicio_inexistente(client: TestClient) -> None:
    sesion = _crear_sesion(client)

    respuesta = client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": 999999, "peso": 80.0, "repeticiones": 8},
    )

    assert respuesta.status_code == 404


def test_listar_series(client: TestClient) -> None:
    sesion = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    _crear_serie(client, sesion["id"], ejercicio["id"], peso=80.0)
    _crear_serie(client, sesion["id"], ejercicio["id"], peso=85.0)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}/series/")

    assert respuesta.status_code == 200
    pesos = {serie["peso"] for serie in respuesta.json()}
    assert pesos == {80.0, 85.0}


def test_listar_series_sesion_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/sesiones/999999/series/")

    assert respuesta.status_code == 404


def test_obtener_serie_por_id(client: TestClient) -> None:
    sesion = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"])

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_serie_inexistente(client: TestClient) -> None:
    sesion = _crear_sesion(client)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}/series/999999")

    assert respuesta.status_code == 404


def test_obtener_serie_de_otra_sesion(client: TestClient) -> None:
    sesion_1 = _crear_sesion(client)
    sesion_2 = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion_1["id"], ejercicio["id"])

    respuesta = client.get(f"/api/v1/sesiones/{sesion_2['id']}/series/{creada['id']}")

    assert respuesta.status_code == 404


def test_actualizar_serie_parcial(client: TestClient) -> None:
    sesion = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"], peso=80.0)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}", json={"peso": 85.0}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["peso"] == 85.0
    assert cuerpo["repeticiones"] == creada["repeticiones"]


def test_actualizar_serie_ejercicio_inexistente(client: TestClient) -> None:
    sesion = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"])

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}", json={"ejercicio_id": 999999}
    )

    assert respuesta.status_code == 404


def test_eliminar_serie(client: TestClient) -> None:
    sesion = _crear_sesion(client)
    ejercicio = _crear_ejercicio(client)
    creada = _crear_serie(client, sesion["id"], ejercicio["id"])

    respuesta_delete = client.delete(f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/sesiones/{sesion['id']}/series/{creada['id']}")
    assert respuesta_get.status_code == 404
