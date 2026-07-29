from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_admin_autenticado, crear_usuario_autenticado


def _crear_grupo_muscular(client: TestClient, headers: dict, nombre: str) -> dict:
    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": nombre}, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_ejercicio(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"nombre": "Press banca", "tipo": "compuesto", "grupos_musculares": []}
    payload.update(overrides)
    respuesta = client.post("/api/v1/ejercicios/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_ejercicio_sin_grupos_musculares(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)

    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={"nombre": "Curl", "tipo": "aislamiento", "grupos_musculares": []},
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Curl"
    assert cuerpo["grupos_musculares"] == []


def test_crear_ejercicio_requiere_admin(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={"nombre": "Curl", "tipo": "aislamiento", "grupos_musculares": []},
        headers=headers,
    )

    assert respuesta.status_code == 403


def test_crear_ejercicio_sin_token(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={"nombre": "Curl", "tipo": "aislamiento", "grupos_musculares": []},
    )

    assert respuesta.status_code == 401


def test_crear_ejercicio_con_grupos_musculares(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    pecho = _crear_grupo_muscular(client, headers, "pecho")
    triceps = _crear_grupo_muscular(client, headers, "triceps")

    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={
            "nombre": "Press banca",
            "tipo": "compuesto",
            "grupos_musculares": [
                {"grupo_muscular_id": pecho["id"], "es_principal": True},
                {"grupo_muscular_id": triceps["id"], "es_principal": False},
            ],
        },
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    asociaciones = {
        (grupo["grupo_muscular"]["nombre"], grupo["es_principal"])
        for grupo in cuerpo["grupos_musculares"]
    }
    assert asociaciones == {("pecho", True), ("triceps", False)}


def test_crear_ejercicio_grupo_muscular_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)

    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={
            "nombre": "Press banca",
            "tipo": "compuesto",
            "grupos_musculares": [{"grupo_muscular_id": 999999, "es_principal": True}],
        },
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_listar_ejercicios(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    _crear_ejercicio(client, headers_admin, nombre="Sentadilla")
    _crear_ejercicio(client, headers_admin, nombre="Peso muerto")

    # Un usuario normal (no admin) puede leer el catálogo sin problema.
    _, headers = crear_usuario_autenticado(client)
    respuesta = client.get("/api/v1/ejercicios/", headers=headers)

    assert respuesta.status_code == 200
    nombres = {ejercicio["nombre"] for ejercicio in respuesta.json()}
    assert nombres == {"Sentadilla", "Peso muerto"}


def test_listar_ejercicios_sin_token(client: TestClient) -> None:
    respuesta = client.get("/api/v1/ejercicios/")

    assert respuesta.status_code == 401


def test_obtener_ejercicio_por_id(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    creado = _crear_ejercicio(client, headers_admin)

    _, headers = crear_usuario_autenticado(client)
    respuesta = client.get(f"/api/v1/ejercicios/{creado['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_ejercicio_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/ejercicios/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_ejercicio_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    creado = _crear_ejercicio(client, headers, nombre="Remo")

    respuesta = client.patch(
        f"/api/v1/ejercicios/{creado['id']}", json={"tipo": "aislamiento"}, headers=headers
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "aislamiento"
    assert cuerpo["nombre"] == "Remo"
    assert cuerpo["grupos_musculares"] == []


def test_actualizar_ejercicio_requiere_admin(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    creado = _crear_ejercicio(client, headers_admin, nombre="Remo")
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.patch(
        f"/api/v1/ejercicios/{creado['id']}", json={"tipo": "aislamiento"}, headers=headers
    )

    assert respuesta.status_code == 403


def test_actualizar_ejercicio_reemplaza_grupos_musculares(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    pecho = _crear_grupo_muscular(client, headers, "pecho")
    espalda = _crear_grupo_muscular(client, headers, "espalda")
    creado = _crear_ejercicio(
        client,
        headers,
        nombre="Press banca",
        grupos_musculares=[{"grupo_muscular_id": pecho["id"], "es_principal": True}],
    )

    respuesta = client.patch(
        f"/api/v1/ejercicios/{creado['id']}",
        json={"grupos_musculares": [{"grupo_muscular_id": espalda["id"], "es_principal": True}]},
        headers=headers,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["grupos_musculares"]) == 1
    assert cuerpo["grupos_musculares"][0]["grupo_muscular"]["nombre"] == "espalda"


def test_eliminar_ejercicio(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    creado = _crear_ejercicio(client, headers)

    respuesta_delete = client.delete(f"/api/v1/ejercicios/{creado['id']}", headers=headers)
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/ejercicios/{creado['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_ejercicio_requiere_admin(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    creado = _crear_ejercicio(client, headers_admin)
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.delete(f"/api/v1/ejercicios/{creado['id']}", headers=headers)

    assert respuesta.status_code == 403


def test_eliminar_ejercicio_con_grupos_musculares_asociados(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    pecho = _crear_grupo_muscular(client, headers, "pecho")
    creado = _crear_ejercicio(
        client, headers, grupos_musculares=[{"grupo_muscular_id": pecho["id"], "es_principal": True}]
    )

    respuesta = client.delete(f"/api/v1/ejercicios/{creado['id']}", headers=headers)

    assert respuesta.status_code == 204
