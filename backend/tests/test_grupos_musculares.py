from fastapi.testclient import TestClient


def _crear_grupo_muscular(client: TestClient, nombre: str) -> dict:
    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": nombre})
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_grupo_muscular(client: TestClient) -> None:
    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": "espalda"})

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] is not None
    assert cuerpo["nombre"] == "espalda"


def test_crear_grupo_muscular_nombre_duplicado(client: TestClient) -> None:
    _crear_grupo_muscular(client, "hombro")

    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": "hombro"})

    assert respuesta.status_code == 409


def test_listar_grupos_musculares(client: TestClient) -> None:
    _crear_grupo_muscular(client, "biceps")
    _crear_grupo_muscular(client, "triceps")

    respuesta = client.get("/api/v1/grupos-musculares/")

    assert respuesta.status_code == 200
    nombres = {grupo["nombre"] for grupo in respuesta.json()}
    assert nombres == {"biceps", "triceps"}


def test_obtener_grupo_muscular_por_id(client: TestClient) -> None:
    creado = _crear_grupo_muscular(client, "gemelo")

    respuesta = client.get(f"/api/v1/grupos-musculares/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_grupo_muscular_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/grupos-musculares/999999")

    assert respuesta.status_code == 404


def test_actualizar_grupo_muscular_parcial(client: TestClient) -> None:
    creado = _crear_grupo_muscular(client, "abdomen")

    respuesta = client.patch(f"/api/v1/grupos-musculares/{creado['id']}", json={"nombre": "core"})

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "core"


def test_eliminar_grupo_muscular(client: TestClient) -> None:
    creado = _crear_grupo_muscular(client, "antebrazo")

    respuesta_delete = client.delete(f"/api/v1/grupos-musculares/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/grupos-musculares/{creado['id']}")
    assert respuesta_get.status_code == 404


def test_eliminar_grupo_muscular_en_uso(client: TestClient) -> None:
    grupo = _crear_grupo_muscular(client, "cuadriceps")
    client.post(
        "/api/v1/ejercicios/",
        json={
            "nombre": "Sentadilla",
            "tipo": "compuesto",
            "grupos_musculares": [{"grupo_muscular_id": grupo["id"], "es_principal": True}],
        },
    )

    respuesta = client.delete(f"/api/v1/grupos-musculares/{grupo['id']}")

    assert respuesta.status_code == 409
