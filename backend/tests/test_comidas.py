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


def _crear_comida(client: TestClient, usuario_id: int, **overrides) -> dict:
    payload = {"nombre": "Pechuga con arroz", "usuario_id": usuario_id}
    payload.update(overrides)
    respuesta = client.post("/api/v1/comidas/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_comida(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/comidas/",
        json={
            "nombre": "Pechuga con arroz",
            "descripcion": "200g pechuga, 100g arroz",
            "calorias": 450,
            "usuario_id": usuario["id"],
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Pechuga con arroz"
    assert cuerpo["descripcion"] == "200g pechuga, 100g arroz"
    assert cuerpo["calorias"] == 450
    assert cuerpo["usuario_id"] == usuario["id"]


def test_crear_comida_sin_calorias(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/comidas/", json={"nombre": "Batido de proteína", "usuario_id": usuario["id"]}
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["calorias"] is None
    assert cuerpo["descripcion"] is None


def test_crear_comida_usuario_inexistente(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/comidas/", json={"nombre": "Pechuga con arroz", "usuario_id": 999999}
    )

    assert respuesta.status_code == 404


def test_listar_comidas(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    _crear_comida(client, usuario["id"], nombre="Pechuga con arroz")
    _crear_comida(client, usuario["id"], nombre="Avena con fruta")

    respuesta = client.get("/api/v1/comidas/")

    assert respuesta.status_code == 200
    nombres = {comida["nombre"] for comida in respuesta.json()}
    assert nombres == {"Pechuga con arroz", "Avena con fruta"}


def test_obtener_comida_por_id(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_comida(client, usuario["id"])

    respuesta = client.get(f"/api/v1/comidas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_comida_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/comidas/999999")

    assert respuesta.status_code == 404


def test_actualizar_comida_parcial(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_comida(client, usuario["id"], calorias=450)

    respuesta = client.patch(f"/api/v1/comidas/{creada['id']}", json={"calorias": 500})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["calorias"] == 500
    assert cuerpo["nombre"] == creada["nombre"]


def test_eliminar_comida(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_comida(client, usuario["id"])

    respuesta_delete = client.delete(f"/api/v1/comidas/{creada['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/comidas/{creada['id']}")
    assert respuesta_get.status_code == 404


def test_eliminar_comida_en_uso(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    respuesta_plan = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan definición",
            "usuario_id": usuario["id"],
            "dias": [
                {
                    "numero_dia": 1,
                    "franja": "almuerzo",
                    "comida_id": comida["id"],
                    "orden": 1,
                }
            ],
        },
    )
    assert respuesta_plan.status_code == 201

    respuesta = client.delete(f"/api/v1/comidas/{comida['id']}")

    assert respuesta.status_code == 409
