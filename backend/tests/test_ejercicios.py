from fastapi.testclient import TestClient


def _crear_grupo_muscular(client: TestClient, nombre: str) -> dict:
    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": nombre})
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_ejercicio(client: TestClient, **overrides) -> dict:
    payload = {"nombre": "Press banca", "tipo": "compuesto", "grupos_musculares": []}
    payload.update(overrides)
    respuesta = client.post("/api/v1/ejercicios/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_ejercicio_sin_grupos_musculares(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={"nombre": "Curl", "tipo": "aislamiento", "grupos_musculares": []},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Curl"
    assert cuerpo["grupos_musculares"] == []


def test_crear_ejercicio_con_grupos_musculares(client: TestClient) -> None:
    pecho = _crear_grupo_muscular(client, "pecho")
    triceps = _crear_grupo_muscular(client, "triceps")

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
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    asociaciones = {
        (grupo["grupo_muscular"]["nombre"], grupo["es_principal"])
        for grupo in cuerpo["grupos_musculares"]
    }
    assert asociaciones == {("pecho", True), ("triceps", False)}


def test_crear_ejercicio_grupo_muscular_inexistente(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={
            "nombre": "Press banca",
            "tipo": "compuesto",
            "grupos_musculares": [{"grupo_muscular_id": 999999, "es_principal": True}],
        },
    )

    assert respuesta.status_code == 404


def test_listar_ejercicios(client: TestClient) -> None:
    _crear_ejercicio(client, nombre="Sentadilla")
    _crear_ejercicio(client, nombre="Peso muerto")

    respuesta = client.get("/api/v1/ejercicios/")

    assert respuesta.status_code == 200
    nombres = {ejercicio["nombre"] for ejercicio in respuesta.json()}
    assert nombres == {"Sentadilla", "Peso muerto"}


def test_obtener_ejercicio_por_id(client: TestClient) -> None:
    creado = _crear_ejercicio(client)

    respuesta = client.get(f"/api/v1/ejercicios/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_ejercicio_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/ejercicios/999999")

    assert respuesta.status_code == 404


def test_actualizar_ejercicio_parcial(client: TestClient) -> None:
    creado = _crear_ejercicio(client, nombre="Remo")

    respuesta = client.patch(f"/api/v1/ejercicios/{creado['id']}", json={"tipo": "aislamiento"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "aislamiento"
    assert cuerpo["nombre"] == "Remo"
    assert cuerpo["grupos_musculares"] == []


def test_actualizar_ejercicio_reemplaza_grupos_musculares(client: TestClient) -> None:
    pecho = _crear_grupo_muscular(client, "pecho")
    espalda = _crear_grupo_muscular(client, "espalda")
    creado = _crear_ejercicio(
        client,
        nombre="Press banca",
        grupos_musculares=[{"grupo_muscular_id": pecho["id"], "es_principal": True}],
    )

    respuesta = client.patch(
        f"/api/v1/ejercicios/{creado['id']}",
        json={"grupos_musculares": [{"grupo_muscular_id": espalda["id"], "es_principal": True}]},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["grupos_musculares"]) == 1
    assert cuerpo["grupos_musculares"][0]["grupo_muscular"]["nombre"] == "espalda"


def test_eliminar_ejercicio(client: TestClient) -> None:
    creado = _crear_ejercicio(client)

    respuesta_delete = client.delete(f"/api/v1/ejercicios/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/ejercicios/{creado['id']}")
    assert respuesta_get.status_code == 404


def test_eliminar_ejercicio_con_grupos_musculares_asociados(client: TestClient) -> None:
    pecho = _crear_grupo_muscular(client, "pecho")
    creado = _crear_ejercicio(
        client, grupos_musculares=[{"grupo_muscular_id": pecho["id"], "es_principal": True}]
    )

    respuesta = client.delete(f"/api/v1/ejercicios/{creado['id']}")

    assert respuesta.status_code == 204
