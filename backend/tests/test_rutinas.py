from datetime import date

from fastapi.testclient import TestClient

USUARIO_EJEMPLO = {
    "nombre": "Angel",
    "email": "angel@example.com",
    "edad": 25,
    "peso": 75.5,
    "altura": 1.78,
    "sexo": "masculino",
    "objetivo": "volumen",
}


def _crear_usuario(client: TestClient, **overrides) -> dict:
    payload = {**USUARIO_EJEMPLO, **overrides}
    respuesta = client.post("/api/v1/usuarios/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_ejercicio(client: TestClient, nombre: str = "Press banca") -> dict:
    respuesta = client.post(
        "/api/v1/ejercicios/", json={"nombre": nombre, "tipo": "compuesto", "grupos_musculares": []}
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _crear_rutina(client: TestClient, usuario_id: int, **overrides) -> dict:
    payload = {"nombre": "Push day", "usuario_id": usuario_id, "ejercicios": []}
    payload.update(overrides)
    respuesta = client.post("/api/v1/rutinas/", json=payload)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_rutina_sin_ejercicios(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/rutinas/", json={"nombre": "Push day", "usuario_id": usuario["id"], "ejercicios": []}
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Push day"
    assert cuerpo["usuario_id"] == usuario["id"]
    assert cuerpo["ejercicios"] == []


def test_crear_rutina_con_ejercicios(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    press = _crear_ejercicio(client, "Press banca")

    respuesta = client.post(
        "/api/v1/rutinas/",
        json={
            "nombre": "Push day",
            "usuario_id": usuario["id"],
            "ejercicios": [
                {
                    "ejercicio_id": press["id"],
                    "orden": 1,
                    "series_objetivo": 4,
                    "repeticiones_objetivo": 8,
                }
            ],
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert len(cuerpo["ejercicios"]) == 1
    item = cuerpo["ejercicios"][0]
    assert item["ejercicio"]["nombre"] == "Press banca"
    assert item["orden"] == 1
    assert item["series_objetivo"] == 4
    assert item["repeticiones_objetivo"] == 8


def test_crear_rutina_usuario_inexistente(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/rutinas/", json={"nombre": "Push day", "usuario_id": 999999, "ejercicios": []}
    )

    assert respuesta.status_code == 404


def test_crear_rutina_ejercicio_inexistente(client: TestClient) -> None:
    usuario = _crear_usuario(client)

    respuesta = client.post(
        "/api/v1/rutinas/",
        json={
            "nombre": "Push day",
            "usuario_id": usuario["id"],
            "ejercicios": [
                {
                    "ejercicio_id": 999999,
                    "orden": 1,
                    "series_objetivo": 4,
                    "repeticiones_objetivo": 8,
                }
            ],
        },
    )

    assert respuesta.status_code == 404


def test_listar_rutinas(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    _crear_rutina(client, usuario["id"], nombre="Push day")
    _crear_rutina(client, usuario["id"], nombre="Pull day")

    respuesta = client.get("/api/v1/rutinas/")

    assert respuesta.status_code == 200
    nombres = {rutina["nombre"] for rutina in respuesta.json()}
    assert nombres == {"Push day", "Pull day"}


def test_obtener_rutina_por_id(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_rutina(client, usuario["id"])

    respuesta = client.get(f"/api/v1/rutinas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_rutina_inexistente(client: TestClient) -> None:
    respuesta = client.get("/api/v1/rutinas/999999")

    assert respuesta.status_code == 404


def test_actualizar_rutina_parcial(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_rutina(client, usuario["id"], nombre="Push day")

    respuesta = client.patch(f"/api/v1/rutinas/{creada['id']}", json={"nombre": "Push day A"})

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Push day A"


def test_actualizar_rutina_reemplaza_ejercicios(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    press = _crear_ejercicio(client, "Press banca")
    remo = _crear_ejercicio(client, "Remo")
    creada = _crear_rutina(
        client,
        usuario["id"],
        ejercicios=[
            {"ejercicio_id": press["id"], "orden": 1, "series_objetivo": 4, "repeticiones_objetivo": 8}
        ],
    )

    respuesta = client.patch(
        f"/api/v1/rutinas/{creada['id']}",
        json={
            "ejercicios": [
                {
                    "ejercicio_id": remo["id"],
                    "orden": 1,
                    "series_objetivo": 3,
                    "repeticiones_objetivo": 10,
                }
            ]
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["ejercicios"]) == 1
    assert cuerpo["ejercicios"][0]["ejercicio"]["nombre"] == "Remo"


def test_eliminar_rutina(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_rutina(client, usuario["id"])

    respuesta_delete = client.delete(f"/api/v1/rutinas/{creada['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = client.get(f"/api/v1/rutinas/{creada['id']}")
    assert respuesta_get.status_code == 404


def test_eliminar_rutina_con_sesiones_asociadas(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_rutina(client, usuario["id"])
    client.post(f"/api/v1/rutinas/{creada['id']}/iniciar")

    respuesta = client.delete(f"/api/v1/rutinas/{creada['id']}")

    assert respuesta.status_code == 409


def test_iniciar_rutina(client: TestClient) -> None:
    usuario = _crear_usuario(client)
    creada = _crear_rutina(client, usuario["id"])

    respuesta = client.post(f"/api/v1/rutinas/{creada['id']}/iniciar")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["rutina_id"] == creada["id"]
    assert cuerpo["usuario_id"] == usuario["id"]
    assert cuerpo["fecha"] == date.today().isoformat()


def test_iniciar_rutina_inexistente(client: TestClient) -> None:
    respuesta = client.post("/api/v1/rutinas/999999/iniciar")

    assert respuesta.status_code == 404
