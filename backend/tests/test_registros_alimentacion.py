from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_autenticado


def _crear_comida(client: TestClient, headers: dict, nombre: str = "Pechuga con arroz") -> dict:
    respuesta = client.post("/api/v1/comidas/", json={"nombre": nombre}, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_plan_dia(client: TestClient, headers: dict, comida_id: int) -> int:
    respuesta = client.post(
        "/api/v1/planes-alimentacion/",
        json={
            "nombre": "Plan volumen",
            "dias": [
                {"numero_dia": 1, "franja": "desayuno", "comida_id": comida_id, "orden": 1}
            ],
        },
        headers=headers,
    )
    assert respuesta.status_code == 201
    return respuesta.json()["dias"][0]["id"]


def _crear_registro(client: TestClient, headers: dict, comida_id: int, **overrides) -> dict:
    payload = {
        "fecha": "2026-07-28",
        "comida_id": comida_id,
        "completada": True,
        "calorias": 400,
    }
    payload.update(overrides)
    respuesta = client.post("/api/v1/registros-alimentacion/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_registro_con_plan_dia(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    plan_dia_id = _crear_plan_dia(client, headers, comida["id"])

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "plan_dia_id": plan_dia_id,
            "completada": True,
            "calorias": 420,
        },
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plan_dia_id"] == plan_dia_id
    assert cuerpo["calorias"] == 420
    assert cuerpo["completada"] is True


def test_crear_registro_sin_plan_dia(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "completada": False,
            "calorias": 300,
        },
        headers=headers,
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["plan_dia_id"] is None


def test_crear_registro_sin_token(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={"fecha": "2026-07-28", "comida_id": comida["id"], "calorias": 300},
    )

    assert respuesta.status_code == 401


def test_crear_registro_comida_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={"fecha": "2026-07-28", "comida_id": 999999, "calorias": 300},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_crear_registro_plan_dia_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "fecha": "2026-07-28",
            "comida_id": comida["id"],
            "plan_dia_id": 999999,
            "calorias": 300,
        },
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_crear_registro_plan_dia_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    comida_1 = _crear_comida(client, headers_1)
    plan_dia_id = _crear_plan_dia(client, headers_1, comida_1["id"])

    respuesta = client.post(
        "/api/v1/registros-alimentacion/",
        json={
            "fecha": "2026-07-28",
            "comida_id": comida_1["id"],
            "plan_dia_id": plan_dia_id,
            "calorias": 300,
        },
        headers=headers_2,
    )

    assert respuesta.status_code == 404


def test_listar_registros(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    _crear_registro(client, headers, comida["id"], calorias=300)
    _crear_registro(client, headers, comida["id"], calorias=500)

    respuesta = client.get("/api/v1/registros-alimentacion/", headers=headers)

    assert respuesta.status_code == 200
    calorias = {registro["calorias"] for registro in respuesta.json()}
    assert calorias == {300, 500}


def test_listar_registros_no_incluye_los_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    comida_1 = _crear_comida(client, headers_1)
    comida_2 = _crear_comida(client, headers_2)
    _crear_registro(client, headers_1, comida_1["id"], calorias=300)
    _crear_registro(client, headers_2, comida_2["id"], calorias=999)

    respuesta = client.get("/api/v1/registros-alimentacion/", headers=headers_1)

    assert respuesta.status_code == 200
    calorias = {registro["calorias"] for registro in respuesta.json()}
    assert calorias == {300}


def test_obtener_registro_por_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    creado = _crear_registro(client, headers, comida["id"])

    respuesta = client.get(f"/api/v1/registros-alimentacion/{creado['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_registro_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    comida_1 = _crear_comida(client, headers_1)
    creado = _crear_registro(client, headers_1, comida_1["id"])

    respuesta = client.get(f"/api/v1/registros-alimentacion/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_registro_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/registros-alimentacion/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_registro_parcial(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    creado = _crear_registro(client, headers, comida["id"], completada=False)

    respuesta = client.patch(
        f"/api/v1/registros-alimentacion/{creado['id']}",
        json={"completada": True},
        headers=headers,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["completada"] is True
    assert cuerpo["calorias"] == creado["calorias"]


def test_actualizar_registro_comida_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    creado = _crear_registro(client, headers, comida["id"])

    respuesta = client.patch(
        f"/api/v1/registros-alimentacion/{creado['id']}",
        json={"comida_id": 999999},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_eliminar_registro(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    comida = _crear_comida(client, headers)
    creado = _crear_registro(client, headers, comida["id"])

    respuesta_delete = client.delete(
        f"/api/v1/registros-alimentacion/{creado['id']}", headers=headers
    )
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/registros-alimentacion/{creado['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_registro_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    comida_1 = _crear_comida(client, headers_1)
    creado = _crear_registro(client, headers_1, comida_1["id"])

    respuesta = client.delete(f"/api/v1/registros-alimentacion/{creado['id']}", headers=headers_2)

    assert respuesta.status_code == 404
