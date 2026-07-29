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


def _iniciar_rutina(client: TestClient, rutina_id: int, headers: dict) -> dict:
    respuesta = client.post(f"/api/v1/rutinas/{rutina_id}/iniciar", headers=headers)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_obtener_sesion(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8}
        ],
    )
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == sesion["id"]
    assert cuerpo["usuario_id"] == usuario["id"]
    assert cuerpo["completada"] is False
    assert cuerpo["rutina"]["id"] == rutina["id"]
    assert cuerpo["rutina"]["nombre"] == "Push day"
    assert len(cuerpo["rutina"]["ejercicios"]) == 1
    assert cuerpo["rutina"]["ejercicios"][0]["ejercicio"]["nombre"] == "Press banca"
    assert cuerpo["ultimas_series"] == []
    assert cuerpo["series_registradas"] == []


def test_obtener_sesion_incluye_ultima_serie_por_ejercicio(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8}
        ],
    )
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": press["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )

    siguiente_sesion = _iniciar_rutina(client, rutina["id"], headers)
    respuesta = client.get(f"/api/v1/sesiones/{siguiente_sesion['id']}", headers=headers)

    assert respuesta.status_code == 200
    referencia = respuesta.json()["ultimas_series"][0]
    assert referencia["ejercicio_id"] == press["id"]
    assert referencia["peso"] == 80.0
    assert referencia["repeticiones"] == 8


def test_obtener_sesion_incluye_series_ya_registradas_agrupadas_por_ejercicio(
    client: TestClient,
) -> None:
    _, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    remo = _crear_ejercicio(client, "Remo")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8},
            {"ejercicio_id": remo["id"], "orden": 2, "series_objetivo": 3, "repeticiones_objetivo": 8},
        ],
    )
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": press["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )
    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": press["id"], "peso": 82.5, "repeticiones": 6},
        headers=headers,
    )
    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": remo["id"], "peso": 60.0, "repeticiones": 10},
        headers=headers,
    )

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers)

    assert respuesta.status_code == 200
    grupos = {grupo["ejercicio_id"]: grupo["series"] for grupo in respuesta.json()["series_registradas"]}
    assert len(grupos) == 2
    assert [s["peso"] for s in grupos[press["id"]]] == [80.0, 82.5]
    assert [s["repeticiones"] for s in grupos[press["id"]]] == [8, 6]
    assert [s["peso"] for s in grupos[remo["id"]]] == [60.0]


def test_obtener_sesion_no_incluye_series_de_otra_sesion(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8}
        ],
    )
    primera_sesion = _iniciar_rutina(client, rutina["id"], headers)
    client.post(
        f"/api/v1/sesiones/{primera_sesion['id']}/series/",
        json={"ejercicio_id": press["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )
    segunda_sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get(f"/api/v1/sesiones/{segunda_sesion['id']}", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["series_registradas"] == []


def test_obtener_sesion_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    sesion = _iniciar_rutina(client, rutina["id"], headers_1)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers_2)

    assert respuesta.status_code == 404


def test_obtener_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.get("/api/v1/sesiones/999999", headers=headers)

    assert respuesta.status_code == 404


def test_obtener_sesion_sin_token(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}")

    assert respuesta.status_code == 401


def test_actualizar_sesion_cambia_rutina(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers, nombre="Push day")
    rutina_2 = _crear_rutina(client, headers, nombre="Pull day")
    sesion = _iniciar_rutina(client, rutina_1["id"], headers)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}", json={"rutina_id": rutina_2["id"]}, headers=headers
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["rutina_id"] == rutina_2["id"]
    assert cuerpo["fecha"] == sesion["fecha"]
    assert cuerpo["completada"] is False


def test_actualizar_sesion_cambia_fecha(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}", json={"fecha": "2026-08-15"}, headers=headers
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["fecha"] == "2026-08-15"
    assert cuerpo["rutina_id"] == sesion["rutina_id"]


def test_actualizar_sesion_completada_devuelve_409(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers, nombre="Push day")
    rutina_2 = _crear_rutina(client, headers, nombre="Pull day")
    sesion = _iniciar_rutina(client, rutina_1["id"], headers)
    client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}", json={"rutina_id": rutina_2["id"]}, headers=headers
    )

    assert respuesta.status_code == 409


def test_actualizar_sesion_completada_no_cambia_datos(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers, nombre="Push day")
    rutina_2 = _crear_rutina(client, headers, nombre="Pull day")
    sesion = _iniciar_rutina(client, rutina_1["id"], headers)
    client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    client.patch(
        f"/api/v1/sesiones/{sesion['id']}",
        json={"fecha": "2026-08-15", "rutina_id": rutina_2["id"]},
        headers=headers,
    )

    respuesta = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers)
    cuerpo = respuesta.json()
    assert cuerpo["fecha"] == sesion["fecha"]
    assert cuerpo["rutina_id"] == rutina_1["id"]


def test_actualizar_sesion_no_afecta_otras_sesiones(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers, nombre="Push day")
    rutina_2 = _crear_rutina(client, headers, nombre="Pull day")
    sesion_1 = _iniciar_rutina(client, rutina_1["id"], headers)
    sesion_2 = _iniciar_rutina(client, rutina_1["id"], headers)

    client.patch(
        f"/api/v1/sesiones/{sesion_1['id']}", json={"rutina_id": rutina_2["id"]}, headers=headers
    )

    respuesta = client.get(f"/api/v1/sesiones/{sesion_2['id']}", headers=headers)
    assert respuesta.json()["rutina_id"] == rutina_1["id"]


def test_actualizar_sesion_rutina_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}", json={"rutina_id": 999999}, headers=headers
    )

    assert respuesta.status_code == 404


def test_actualizar_sesion_rutina_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers_1)
    rutina_2 = _crear_rutina(client, headers_2)
    sesion = _iniciar_rutina(client, rutina_1["id"], headers_1)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}", json={"rutina_id": rutina_2["id"]}, headers=headers_1
    )

    assert respuesta.status_code == 404


def test_actualizar_sesion_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    sesion = _iniciar_rutina(client, rutina["id"], headers_1)

    respuesta = client.patch(
        f"/api/v1/sesiones/{sesion['id']}", json={"rutina_id": rutina["id"]}, headers=headers_2
    )

    assert respuesta.status_code == 404


def test_actualizar_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.patch(
        "/api/v1/sesiones/999999", json={"rutina_id": 1}, headers=headers
    )

    assert respuesta.status_code == 404


def test_actualizar_sesion_sin_token(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.patch(f"/api/v1/sesiones/{sesion['id']}", json={"rutina_id": rutina["id"]})

    assert respuesta.status_code == 401


def test_finalizar_sesion(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    assert sesion["completada"] is False

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True


def test_finalizar_sesion_es_idempotente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    primera = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)
    segunda = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    assert primera.status_code == 200
    assert segunda.status_code == 200
    assert segunda.json()["completada"] is True


def test_finalizar_sesion_fija_hora_fin(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    assert respuesta.json()["hora_fin"] is not None


def test_finalizar_sesion_sin_series_fija_hora_inicio_igual_a_hora_fin(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    assert sesion["hora_inicio"] is None

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    cuerpo = respuesta.json()
    assert cuerpo["hora_inicio"] is not None
    assert cuerpo["hora_inicio"] == cuerpo["hora_fin"]


def test_finalizar_sesion_no_sobrescribe_hora_inicio_ya_fijada(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    press = _crear_ejercicio(client, "Press banca")
    rutina = _crear_rutina(
        client,
        headers,
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 3, "repeticiones_objetivo": 8}
        ],
    )
    sesion = _iniciar_rutina(client, rutina["id"], headers)
    client.post(
        f"/api/v1/sesiones/{sesion['id']}/series/",
        json={"ejercicio_id": press["id"], "peso": 80.0, "repeticiones": 8},
        headers=headers,
    )
    hora_inicio_tras_serie = client.get(f"/api/v1/sesiones/{sesion['id']}", headers=headers).json()[
        "hora_inicio"
    ]

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    cuerpo = respuesta.json()
    assert cuerpo["hora_inicio"] == hora_inicio_tras_serie
    assert cuerpo["hora_fin"] is not None
    assert cuerpo["hora_fin"] != cuerpo["hora_inicio"]


def test_finalizar_sesion_idempotente_no_cambia_hora_fin(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    primera = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)
    segunda = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers)

    assert primera.json()["hora_fin"] == segunda.json()["hora_fin"]


def test_finalizar_sesion_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers_1)
    sesion = _iniciar_rutina(client, rutina["id"], headers_1)

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar", headers=headers_2)

    assert respuesta.status_code == 404


def test_finalizar_sesion_inexistente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    respuesta = client.post("/api/v1/sesiones/999999/finalizar", headers=headers)

    assert respuesta.status_code == 404


def test_finalizar_sesion_sin_token(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.post(f"/api/v1/sesiones/{sesion['id']}/finalizar")

    assert respuesta.status_code == 401


def test_listar_sesiones(client: TestClient) -> None:
    usuario, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion_1 = _iniciar_rutina(client, rutina["id"], headers)
    sesion_2 = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get("/api/v1/sesiones/", headers=headers)

    assert respuesta.status_code == 200
    ids = {sesion["id"] for sesion in respuesta.json()}
    assert ids == {sesion_1["id"], sesion_2["id"]}
    assert all(sesion["usuario_id"] == usuario["id"] for sesion in respuesta.json())


def test_listar_sesiones_ordenadas_por_fecha_descendente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    sesion_1 = _iniciar_rutina(client, rutina["id"], headers)
    sesion_2 = _iniciar_rutina(client, rutina["id"], headers)
    sesion_3 = _iniciar_rutina(client, rutina["id"], headers)

    respuesta = client.get("/api/v1/sesiones/", headers=headers)

    assert respuesta.status_code == 200
    ids_en_orden = [sesion["id"] for sesion in respuesta.json()]
    # Todas se crean el mismo día en el test, así que el desempate es por id
    # descendente (la más reciente primero).
    assert ids_en_orden == [sesion_3["id"], sesion_2["id"], sesion_1["id"]]


def test_listar_sesiones_filtra_por_rutina_id(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers, nombre="Push day")
    rutina_2 = _crear_rutina(client, headers, nombre="Pull day")
    sesion_1 = _iniciar_rutina(client, rutina_1["id"], headers)
    _iniciar_rutina(client, rutina_2["id"], headers)

    respuesta = client.get(f"/api/v1/sesiones/?rutina_id={rutina_1['id']}", headers=headers)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["id"] == sesion_1["id"]


def test_listar_sesiones_no_incluye_las_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers_1)
    rutina_2 = _crear_rutina(client, headers_2)
    sesion_1 = _iniciar_rutina(client, rutina_1["id"], headers_1)
    _iniciar_rutina(client, rutina_2["id"], headers_2)

    respuesta = client.get("/api/v1/sesiones/", headers=headers_1)

    assert respuesta.status_code == 200
    ids = [sesion["id"] for sesion in respuesta.json()]
    assert ids == [sesion_1["id"]]


def test_listar_sesiones_sin_token(client: TestClient) -> None:
    respuesta = client.get("/api/v1/sesiones/")

    assert respuesta.status_code == 401
