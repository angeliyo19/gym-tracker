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


def _crear_plan(client: TestClient, usuario_id: int, **overrides) -> dict:
    payload = {"nombre": "Plan volumen", "usuario_id": usuario_id, "dias": []}
    payload.update(overrides)
    respuesta = client.post("/api/v1/planes-alimentacion/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_plan_sin_dias(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={"nombre": "Plan volumen", "usuario_id": usuario["id"], "dias": []},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Plan volumen"
    assert cuerpo["dias"] == []


def test_crear_plan_con_dias(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    desayuno = _crear_comida(client, usuario["id"], "Avena con fruta")
    almuerzo = _crear_comida(client, usuario["id"], "Pechuga con arroz")

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "usuario_id": usuario["id"],
            "dias": [
                {
                    "numero_dia": 1,
                    "franja": "desayuno",
                    "comida_id": desayuno["id"],
                    "orden": 1,
                },
                {
                    "numero_dia": 1,
                    "franja": "almuerzo",
                    "comida_id": almuerzo["id"],
                    "orden": 1,
                },
            ],
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    franjas = {(dia["franja"], dia["comida"]["nombre"]) for dia in cuerpo["dias"]}
    assert franjas == {("desayuno", "Avena con fruta"), ("almuerzo", "Pechuga con arroz")}


def test_crear_plan_usuario_inexistente(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={"nombre": "Plan volumen", "usuario_id": 999999, "dias": []},
    )

    assert respuesta.status_code == 404


def test_crear_plan_comida_inexistente(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "usuario_id": usuario["id"],
            "dias": [
                {"numero_dia": 1, "franja": "desayuno", "comida_id": 999999, "orden": 1}
            ],
        },
    )

    assert respuesta.status_code == 404


def test_crear_plan_franja_invalida(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "usuario_id": usuario["id"],
            "dias": [
                {
                    "numero_dia": 1,
                    "franja": "brunch",
                    "comida_id": comida["id"],
                    "orden": 1,
                }
            ],
        },
    )

    assert respuesta.status_code == 422


def test_listar_planes(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    _crear_plan(client, usuario["id"], nombre="Plan volumen")
    _crear_plan(client, usuario["id"], nombre="Plan definición")

    respuesta = client.get("/api/v1/planes-alimentacion/")

    assert respuesta.status_code == 200
    nombres = {plan["nombre"] for plan in respuesta.json()}
    assert nombres == {"Plan volumen", "Plan definición"}


def test_obtener_plan_por_id(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creado = _crear_plan(client, usuario["id"])

    respuesta = client.get(f"/api/v1/planes-alimentacion/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_plan_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/planes-alimentacion/999999")

    assert respuesta.status_code == 404


def test_actualizar_plan_parcial(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creado = _crear_plan(client, usuario["id"], nombre="Plan volumen")

    respuesta = client.patch(
        f"/api/v1/planes-alimentacion/{creado['id']}", json={"nombre": "Plan volumen v2"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Plan volumen v2"


def test_actualizar_plan_reemplaza_dias(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    desayuno = _crear_comida(client, usuario["id"], "Avena con fruta")
    cena = _crear_comida(client, usuario["id"], "Pescado con verduras")
    creado = _crear_plan(
        client,
        usuario["id"],
        dias=[{"numero_dia": 1, "franja": "desayuno", "comida_id": desayuno["id"], "orden": 1}],
    )

    respuesta = client.patch(
        f"/api/v1/planes-alimentacion/{creado['id']}",
        json={
            "dias": [
                {"numero_dia": 1, "franja": "cena", "comida_id": cena["id"], "orden": 1}
            ]
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["dias"]) == 1
    assert cuerpo["dias"][0]["franja"] == "cena"
    assert cuerpo["dias"][0]["comida"]["nombre"] == "Pescado con verduras"


def test_actualizar_plan_dias_con_registro_asociado(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    desayuno = _crear_comida(client, usuario["id"], "Avena con fruta")
    cena = _crear_comida(client, usuario["id"], "Pescado con verduras")
    creado = _crear_plan(
        client,
        usuario["id"],
        dias=[{"numero_dia": 1, "franja": "desayuno", "comida_id": desayuno["id"], "orden": 1}],
    )
    plan_dia_id = creado["dias"][0]["id"]

    respuesta_registro = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "comida_id": desayuno["id"],
            "plan_dia_id": plan_dia_id,
            "completada": True,
            "calorias": 300,
        },
    )
    assert respuesta_registro.status_code == 201

    respuesta = client.patch(
        f"/api/v1/planes-alimentacion/{creado['id']}",
        json={
            "dias": [
                {"numero_dia": 1, "franja": "cena", "comida_id": cena["id"], "orden": 1}
            ]
        },
    )

    assert respuesta.status_code == 409


def test_eliminar_plan(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creado = _crear_plan(client, usuario["id"])

    respuesta_delete = client.delete(f"/api/v1/planes-alimentacion/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/planes-alimentacion/{creado['id']}")
    assert respuesta_get.status_code == 404


def test_eliminar_plan_con_registros_asociados(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    comida = _crear_comida(client, usuario["id"])
    creado = _crear_plan(
        client,
        usuario["id"],
        dias=[{"numero_dia": 1, "franja": "desayuno", "comida_id": comida["id"], "orden": 1}],
    )
    plan_dia_id = creado["dias"][0]["id"]

    respuesta_registro = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "usuario_id": usuario["id"],
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "plan_dia_id": plan_dia_id,
            "completada": True,
            "calorias": 400,
        },
    )
    assert respuesta_registro.status_code == 201

    respuesta = client.delete(f"/api/v1/planes-alimentacion/{creado['id']}")

    assert respuesta.status_code == 409
