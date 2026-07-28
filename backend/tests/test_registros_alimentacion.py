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


def _crear_comida(client: TestClient, usuario_id: int, nombre: str = "Pechuga con arroz") -> dict:
    respuesta = client.post("/api/v1/comidas/", json={"nombre": nombre, "usuario_id": usuario_id})
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_plan_dia(client: TestClient, usuario_id: int, comida_id: int) -> int:
    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "usuario_id": usuario_id,
            "dias": [
                {"numero_dia": 1, "franja": "desayuno", "comida_id": comida_id, "orden": 1}
            ],
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()["dias"][0]["id"]


def _crear_registro(client: TestClient, usuario_id: int, comida_id: int, **overrides) -> dict:
    payload = {
        "usuario_id": usuario_id,
        "fecha": "2026-07-28",
        "comida_id": comida_id,
        "completada": True,
        "calorias": 400,
    }
    payload.update(overrides)
    respuesta = client.post("/api/v1/registros-alimentacion/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_registro_con_plan_dia(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    plan_dia_id = _crear_plan_dia(client, usuario["id"], comida["id"])

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "plan_dia_id": plan_dia_id,
            "completada": True,
            "calorias": 420,
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plan_dia_id"] == plan_dia_id
    assert cuerpo["calorias"] == 420
    assert cuerpo["completada"] is True


def test_crear_registro_sin_plan_dia(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "completada": False,
            "calorias": 300,
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["plan_dia_id"] is None


def test_crear_registro_usuario_inexistente(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": 999999,
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "calorias": 300,
        },
    )

    assert respuesta.status_code == 404


def test_crear_registro_comida_inexistente(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "comida_id": 999999,
            "calorias": 300,
        },
    )

    assert respuesta.status_code == 404


def test_crear_registro_plan_dia_inexistente(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "plan_dia_id": 999999,
            "calorias": 300,
        },
    )

    assert respuesta.status_code == 404


def test_listar_registros(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    _crear_registro(client, usuario["id"], comida["id"], calorias=300)
    _crear_registro(client, usuario["id"], comida["id"], calorias=500)

    respuesta = client.get("/api/v1/registros-alimentacion/")

    assert respuesta.status_code == 200
    calorias = {registro["calorias"] for registro in respuesta.json()}
    assert calorias == {300, 500}


def test_obtener_registro_por_id(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    creado = _crear_registro(client, usuario["id"], comida["id"])

    respuesta = client.get(f"/api/v1/registros-alimentacion/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_registro_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/registros-alimentacion/999999")

    assert respuesta.status_code == 404


def test_actualizar_registro_parcial(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    creado = _crear_registro(client, usuario["id"], comida["id"], completada=False)

    respuesta = client.patch(
        f"/api/v1/registros-alimentacion/{creado['id']}", json={"completada": True}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["completada"] is True
    assert cuerpo["calorias"] == creado["calorias"]


def test_actualizar_registro_comida_inexistente(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    creado = _crear_registro(client, usuario["id"], comida["id"])

    respuesta = client.patch(
        f"/api/v1/registros-alimentacion/{creado['id']}", json={"comida_id": 999999}
    )

    assert respuesta.status_code == 404


def test_eliminar_registro(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    creado = _crear_registro(client, usuario["id"], comida["id"])

    respuesta_delete = client.delete(f"/api/v1/registros-alimentacion/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/registros-alimentacion/{creado['id']}")
    assert respuesta_get.status_code == 404
