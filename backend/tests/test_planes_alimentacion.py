from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_comida(client: TestClient, headers: dict, nombre: str = "Pechuga con arroz") -> dict:
    respuesta = client.post("/api/v1/comidas/", json={"nombre": nombre}, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_plan(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"nombre": "Plan volumen", "dias": []}
    payload.update(overrides)
    respuesta = client.post("/api/v1/planes-alimentacion/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_plan_sin_dias(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={"nombre": "Plan volumen", "dias": []},
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Plan volumen"
    assert cuerpo["dias"] == []


def test_crear_plan_sin_token(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/planes-alimentacion/", json={"nombre": "Plan volumen", "dias": []}
    )

    assert respuesta.status_code == 401


def test_crear_plan_con_dias(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    desayuno = _crear_comida(client, headers, "Avena con fruta")
    almuerzo = _crear_comida(client, headers, "Pechuga con arroz")

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
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
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    franjas = {(dia["franja"], dia["comida"]["nombre"]) for dia in cuerpo["dias"]}
    assert franjas == {("desayuno", "Avena con fruta"), ("almuerzo", "Pechuga con arroz")}


def test_crear_plan_comida_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "dias": [
                {"numero_dia": 1, "franja": "desayuno", "comida_id": 999999, "orden": 1}
            ],
        },
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_crear_plan_franja_invalida(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)

    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "dias": [
                {
                    "numero_dia": 1,
                    "franja": "brunch",
                    "comida_id": comida["id"],
                    "orden": 1,
                }
            ],
        },
        headers=headers,
    )

    assert respuesta.status_code == 422


def test_listar_planes(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    _crear_plan(client, headers, nombre="Plan volumen")
    _crear_plan(client, headers, nombre="Plan definición")

    respuesta = client.get("/api/v1/planes-alimentacion/", headers=headers)

    assert respuesta.status_code == 200
    nombres = {plan["nombre"] for plan in respuesta.json()}
    assert nombres == {"Plan volumen", "Plan definición"}


def test_listar_planes_no_incluye_los_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    _crear_plan(client, headers_1, nombre="Plan volumen")
    _crear_plan(client, headers_2, nombre="Plan definición")

    respuesta = client.get("/api/v1/planes-alimentacion/", headers=headers_1)

    assert respuesta.status_code == 200
    nombres = {plan["nombre"] for plan in respuesta.json()}
    assert nombres == {"Plan volumen"}


def test_obtener_plan_por_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_plan(client, headers)

    respuesta = client.get(f"/api/v1/planes-alimentacion/{creado['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_plan_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creado = _crear_plan(client, headers_1)

    respuesta = client.get(f"/api/v1/planes-alimentacion/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_plan_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/planes-alimentacion/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_plan_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_plan(client, headers, nombre="Plan volumen")

    respuesta = client.patch(
        f"/api/v1/planes-alimentacion/{creado['id']}",
        json={"nombre": "Plan volumen v2"},
        headers=headers,
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Plan volumen v2"


def test_actualizar_plan_reemplaza_dias(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    desayuno = _crear_comida(client, headers, "Avena con fruta")
    cena = _crear_comida(client, headers, "Pescado con verduras")
    creado = _crear_plan(
        client,
        headers,
        dias=[{"numero_dia": 1, "franja": "desayuno", "comida_id": desayuno["id"], "orden": 1}],
    )

    respuesta = client.patch(
        f"/api/v1/planes-alimentacion/{creado['id']}",
        json={
            "dias": [
                {"numero_dia": 1, "franja": "cena", "comida_id": cena["id"], "orden": 1}
            ]
        },
        headers=headers,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["dias"]) == 1
    assert cuerpo["dias"][0]["franja"] == "cena"
    assert cuerpo["dias"][0]["comida"]["nombre"] == "Pescado con verduras"


def test_actualizar_plan_dias_con_registro_asociado(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    desayuno = _crear_comida(client, headers, "Avena con fruta")
    cena = _crear_comida(client, headers, "Pescado con verduras")
    creado = _crear_plan(
        client,
        headers,
        dias=[{"numero_dia": 1, "franja": "desayuno", "comida_id": desayuno["id"], "orden": 1}],
    )
    plan_dia_id = creado["dias"][0]["id"]

    respuesta_registro = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "fecha": "2026-07-28",
            "comida_id": desayuno["id"],
            "plan_dia_id": plan_dia_id,
            "completada": True,
            "calorias": 300,
        },
        headers=headers,
    )
    assert respuesta_registro.status_code == 201

    respuesta = client.patch(
        f"/api/v1/planes-alimentacion/{creado['id']}",
        json={
            "dias": [
                {"numero_dia": 1, "franja": "cena", "comida_id": cena["id"], "orden": 1}
            ]
        },
        headers=headers,
    )

    assert respuesta.status_code == 409


def test_eliminar_plan(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    creado = _crear_plan(client, headers)

    respuesta_delete = client.delete(f"/api/v1/planes-alimentacion/{creado['id']}", headers=headers)
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/planes-alimentacion/{creado['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_plan_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    creado = _crear_plan(client, headers_1)

    respuesta = client.delete(f"/api/v1/planes-alimentacion/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_eliminar_plan_con_registros_asociados(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    creado = _crear_plan(
        client,
        headers,
        dias=[{"numero_dia": 1, "franja": "desayuno", "comida_id": comida["id"], "orden": 1}],
    )
    plan_dia_id = creado["dias"][0]["id"]

    respuesta_registro = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "plan_dia_id": plan_dia_id,
            "completada": True,
            "calorias": 400,
        },
        headers=headers,
    )
    assert respuesta_registro.status_code == 201

    respuesta = client.delete(f"/api/v1/planes-alimentacion/{creado['id']}", headers=headers)

    assert respuesta.status_code == 409
