from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_admin_autenticado, crear_usuario_autenticado


def _crear_grupo_muscular(client: TestClient, headers: dict, nombre: str) -> dict:
    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": nombre}, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_grupo_muscular(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)

    respuesta = client.post(
        "/api/v1/grupos-musculares/", json={"nombre": "espalda"}, headers=headers
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] is not None
    assert cuerpo["nombre"] == "espalda"


def test_crear_grupo_muscular_requiere_admin(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/grupos-musculares/", json={"nombre": "espalda"}, headers=headers
    )

    assert respuesta.status_code == 403


def test_crear_grupo_muscular_sin_token(client: TestClient) -> None:
    respuesta = client.post("/api/v1/grupos-musculares/", json={"nombre": "espalda"})

    assert respuesta.status_code == 401


def test_crear_grupo_muscular_nombre_duplicado(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    _crear_grupo_muscular(client, headers, "hombro")

    respuesta = client.post(
        "/api/v1/grupos-musculares/", json={"nombre": "hombro"}, headers=headers
    )

    assert respuesta.status_code == 409


def test_listar_grupos_musculares(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    _crear_grupo_muscular(client, headers_admin, "biceps")
    _crear_grupo_muscular(client, headers_admin, "triceps")

    # Un usuario normal (no admin) puede leer el catálogo sin problema.
    _, headers = crear_usuario_autenticado(client)
    respuesta = client.get("/api/v1/grupos-musculares/", headers=headers)

    assert respuesta.status_code == 200
    nombres = {grupo["nombre"] for grupo in respuesta.json()}
    assert nombres == {"biceps", "triceps"}


def test_listar_grupos_musculares_sin_token(client: TestClient) -> None:
    respuesta = client.get("/api/v1/grupos-musculares/")

    assert respuesta.status_code == 401


def test_obtener_grupo_muscular_por_id(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    creado = _crear_grupo_muscular(client, headers_admin, "gemelo")

    _, headers = crear_usuario_autenticado(client)
    respuesta = client.get(f"/api/v1/grupos-musculares/{creado['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_grupo_muscular_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/grupos-musculares/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_grupo_muscular_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    creado = _crear_grupo_muscular(client, headers, "abdomen")

    respuesta = client.patch(
        f"/api/v1/grupos-musculares/{creado['id']}", json={"nombre": "core"}, headers=headers
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "core"


def test_actualizar_grupo_muscular_requiere_admin(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    creado = _crear_grupo_muscular(client, headers_admin, "abdomen")
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.patch(
        f"/api/v1/grupos-musculares/{creado['id']}", json={"nombre": "core"}, headers=headers
    )

    assert respuesta.status_code == 403


def test_eliminar_grupo_muscular(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    creado = _crear_grupo_muscular(client, headers, "antebrazo")

    respuesta_delete = client.delete(f"/api/v1/grupos-musculares/{creado['id']}", headers=headers)
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/grupos-musculares/{creado['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_grupo_muscular_requiere_admin(client: TestClient) -> None:
    _, headers_admin = crear_usuario_admin_autenticado(client)
    creado = _crear_grupo_muscular(client, headers_admin, "antebrazo")
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.delete(f"/api/v1/grupos-musculares/{creado['id']}", headers=headers)

    assert respuesta.status_code == 403


def test_eliminar_grupo_muscular_en_uso(client: TestClient) -> None:
    _, headers = crear_usuario_admin_autenticado(client)
    grupo = _crear_grupo_muscular(client, headers, "cuadriceps")
    client.post(
        "/api/v1/ejercicios/",
        json={
            "nombre": "Sentadilla",
            "tipo": "compuesto",
            "grupos_musculares": [{"grupo_muscular_id": grupo["id"], "es_principal": True}],
        },
        headers=headers,
    )

    respuesta = client.delete(f"/api/v1/grupos-musculares/{grupo['id']}", headers=headers)

    assert respuesta.status_code == 409
