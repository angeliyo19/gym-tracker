from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_comida(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"nombre": "Pechuga con arroz"}
    payload.update(overrides)
    respuesta = client.post("/api/v1/comidas/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_comida(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/comidas/",
        json={
            "nombre": "Pechuga con arroz",
            "descripcion": "200g pechuga, 100g arroz",
            "calorias": 450,
        },
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Pechuga con arroz"
    assert cuerpo["descripcion"] == "200g pechuga, 100g arroz"
    assert cuerpo["calorias"] == 450
    assert cuerpo["usuario_id"] == usuario["id"]


def test_crear_comida_sin_calorias(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/comidas/", json={"nombre": "Batido de proteína"}, headers=headers
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["calorias"] is None
    assert cuerpo["descripcion"] is None


def test_crear_comida_sin_token(client: TestClient) -> None:
    respuesta = client.post("/api/v1/comidas/", json={"nombre": "Pechuga con arroz"})

    assert respuesta.status_code == 401


def test_listar_comidas(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    _crear_comida(client, headers, nombre="Pechuga con arroz")
    _crear_comida(client, headers, nombre="Avena con fruta")

    respuesta = client.get("/api/v1/comidas/", headers=headers)

    assert respuesta.status_code == 200
    nombres = {comida["nombre"] for comida in respuesta.json()}
    assert nombres == {"Pechuga con arroz", "Avena con fruta"}


def test_listar_comidas_no_incluye_las_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    _crear_comida(client, headers_1, nombre="Pechuga con arroz")
    _crear_comida(client, headers_2, nombre="Avena con fruta")

    respuesta = client.get("/api/v1/comidas/", headers=headers_1)

    assert respuesta.status_code == 200
    nombres = {comida["nombre"] for comida in respuesta.json()}
    assert nombres == {"Pechuga con arroz"}


def test_obtener_comida_por_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creada = _crear_comida(client, headers)

    respuesta = client.get(f"/api/v1/comidas/{creada['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_comida_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creada = _crear_comida(client, headers_1)

    respuesta = client.get(f"/api/v1/comidas/{creada['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_comida_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/comidas/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_comida_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creada = _crear_comida(client, headers, calorias=450)

    respuesta = client.patch(
        f"/api/v1/comidas/{creada['id']}", json={"calorias": 500}, headers=headers
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["calorias"] == 500
    assert cuerpo["nombre"] == creada["nombre"]


def test_actualizar_comida_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creada = _crear_comida(client, headers_1)

    respuesta = client.patch(
        f"/api/v1/comidas/{creada['id']}", json={"calorias": 999}, headers=headers_2
    )

    assert respuesta.status_code == 404


def test_eliminar_comida(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creada = _crear_comida(client, headers)

    respuesta_delete = client.delete(f"/api/v1/comidas/{creada['id']}", headers=headers)
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/comidas/{creada['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_comida_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creada = _crear_comida(client, headers_1)

    respuesta = client.delete(f"/api/v1/comidas/{creada['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_eliminar_comida_en_uso(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    respuesta_plan = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan definición",
            "dias": [
                {
                    "numero_dia": 1,
                    "franja": "almuerzo",
                    "comida_id": comida["id"],
                    "orden": 1,
                }
            ],
        },
        headers=headers,
    )
    assert respuesta_plan.status_code == 201

    respuesta = client.delete(f"/api/v1/comidas/{comida['id']}", headers=headers)

    assert respuesta.status_code == 409
