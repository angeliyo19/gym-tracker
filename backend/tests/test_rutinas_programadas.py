from fastapi.testclient import TestClient

from tests.conftest import crear_usuario_admin_autenticado, crear_usuario_autenticado


def _crear_ejercicio(client: TestClient, nombre: str = "Press banca") -> dict:
    # Crear un ejercicio requiere rol admin; se usa un admin de usar-y-tirar
    # ajeno al usuario "normal" que protagoniza cada test, ya que el catálogo
    # de ejercicios no pertenece a ningún usuario en particular.
    _, headers_admin = crear_usuario_admin_autenticado(client)
    respuesta = client.post(
        "/api/v1/ejercicios/",
        json={"nombre": nombre, "tipo": "compuesto", "grupos_musculares": []},
        headers=headers_admin,
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_rutina(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"nombre": "Push day"}
    if "ejercicios" not in overrides:
        ejercicio = _crear_ejercicio(client)
        payload["ejercicios"] = [
            {
                "ejercicio_id": ejercicio["id"],
                "orden": 1,
                "series_objetivo": 3,
                "repeticiones_objetivo": 10,
            }
        ]
    payload.update(overrides)
    respuesta = client.post("/api/v1/rutinas/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_programada(client: TestClient, headers: dict, rutina_id: int, **overrides) -> dict:
    payload = {"dia_semana": "lunes", "rutina_id": rutina_id}
    payload.update(overrides)
    respuesta = client.post("/api/v1/rutinas-programadas/", json=payload, headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_rutina_programada(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)

    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": "lunes", "rutina_id": rutina["id"]},
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dia_semana"] == "lunes"
    assert cuerpo["rutina_id"] == rutina["id"]
    assert cuerpo["usuario_id"] == usuario["id"]


def test_crear_rutina_programada_dia_invalido(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)

    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": "funday", "rutina_id": rutina["id"]},
        headers=headers,
    )

    assert respuesta.status_code == 422


def test_crear_rutina_programada_rutina_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": "lunes", "rutina_id": 999999},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_crear_rutina_programada_rutina_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)

    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": "lunes", "rutina_id": rutina["id"]},
        headers=headers_2,
    )

    assert respuesta.status_code == 404


def test_crear_rutina_programada_duplicada_mismo_dia(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers, nombre="Push day")
    rutina_2 = _crear_rutina(client, headers, nombre="Pull day")
    _crear_programada(client, headers, rutina_1["id"], dia_semana="lunes")

    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": "lunes", "rutina_id": rutina_2["id"]},
        headers=headers,
    )

    assert respuesta.status_code == 409


def test_crear_rutina_programada_mismo_dia_distinto_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers_1)
    rutina_2 = _crear_rutina(client, headers_2)
    _crear_programada(client, headers_1, rutina_1["id"], dia_semana="lunes")

    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": "lunes", "rutina_id": rutina_2["id"]},
        headers=headers_2,
    )

    assert respuesta.status_code == 201


def test_crear_rutina_programada_sin_token(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/rutinas-programadas/", json={"dia_semana": "lunes", "rutina_id": 1}
    )

    assert respuesta.status_code == 401


def test_listar_rutinas_programadas(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    _crear_programada(client, headers, rutina["id"], dia_semana="lunes")
    _crear_programada(client, headers, rutina["id"], dia_semana="martes")

    respuesta = client.get("/api/v1/rutinas-programadas/", headers=headers)

    assert respuesta.status_code == 200
    dias = {p["dia_semana"] for p in respuesta.json()}
    assert dias == {"lunes", "martes"}


def test_listar_rutinas_programadas_no_incluye_las_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers_1)
    rutina_2 = _crear_rutina(client, headers_2)
    _crear_programada(client, headers_1, rutina_1["id"], dia_semana="lunes")
    _crear_programada(client, headers_2, rutina_2["id"], dia_semana="martes")

    respuesta = client.get("/api/v1/rutinas-programadas/", headers=headers_1)

    assert respuesta.status_code == 200
    dias = {p["dia_semana"] for p in respuesta.json()}
    assert dias == {"lunes"}


def test_obtener_rutina_programada_por_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    creada = _crear_programada(client, headers, rutina["id"])

    respuesta = client.get(f"/api/v1/rutinas-programadas/{creada['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_rutina_programada_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    creada = _crear_programada(client, headers_1, rutina["id"])

    respuesta = client.get(f"/api/v1/rutinas-programadas/{creada['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_rutina_programada_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/rutinas-programadas/999999", headers=headers)

    assert respuesta.status_code == 404


def test_actualizar_rutina_programada_cambia_dia(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    creada = _crear_programada(client, headers, rutina["id"], dia_semana="lunes")

    respuesta = client.patch(
        f"/api/v1/rutinas-programadas/{creada['id']}",
        json={"dia_semana": "miércoles"},
        headers=headers,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["dia_semana"] == "miércoles"
    assert cuerpo["rutina_id"] == rutina["id"]


def test_actualizar_rutina_programada_rutina_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    creada = _crear_programada(client, headers, rutina["id"])

    respuesta = client.patch(
        f"/api/v1/rutinas-programadas/{creada['id']}",
        json={"rutina_id": 999999},
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_actualizar_rutina_programada_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    creada = _crear_programada(client, headers_1, rutina["id"])

    respuesta = client.patch(
        f"/api/v1/rutinas-programadas/{creada['id']}",
        json={"dia_semana": "martes"},
        headers=headers_2,
    )

    assert respuesta.status_code == 404


def test_eliminar_rutina_programada(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    creada = _crear_programada(client, headers, rutina["id"])

    respuesta_delete = client.delete(
        f"/api/v1/rutinas-programadas/{creada['id']}", headers=headers
    )
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/rutinas-programadas/{creada['id']}", headers=headers)
    assert respuesta_get.status_code == 404


def test_eliminar_rutina_programada_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    creada = _crear_programada(client, headers_1, rutina["id"])

    respuesta = client.delete(f"/api/v1/rutinas-programadas/{creada['id']}", headers=headers_2)

    assert respuesta.status_code == 404
