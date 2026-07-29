from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.schemas.rutina_programada import DIAS_SEMANA
from tests.conftest import crear_usuario_autenticado

HOY = date.today()
DIA_SEMANA_HOY = DIAS_SEMANA[HOY.weekday()]


def _crear_ejercicio(client: TestClient, nombre: str = "Press banca") -> dict:
    respuesta = client.post(
        "/api/v1/ejercicios/", json={"nombre": nombre, "tipo": "compuesto", "grupos_musculares": []}
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


def _programar(client: TestClient, headers: dict, dia_semana: str, rutina_id: int) -> dict:
    respuesta = client.post(
        "/api/v1/rutinas-programadas/",
        json={"dia_semana": dia_semana, "rutina_id": rutina_id},
        headers=headers,
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _obtener_calendario(client: TestClient, headers: dict, desde: date, hasta: date) -> list[dict]:
    respuesta = client.get(
        f"/api/v1/calendario?desde={desde.isoformat()}&hasta={hasta.isoformat()}",
        headers=headers,
    )
    assert respuesta.status_code == 200
    return respuesta.json()


def test_calendario_sin_rutinas_programadas_no_crea_sesiones(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)

    cuerpo = _obtener_calendario(client, headers, HOY, HOY + timedelta(days=27))

    assert cuerpo == []


def test_calendario_rellena_huecos_segun_rutina_programada(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    _programar(client, headers, DIA_SEMANA_HOY, rutina["id"])

    cuerpo = _obtener_calendario(client, headers, HOY, HOY + timedelta(days=27))

    # El día de hoy de la semana cae exactamente 4 veces en una ventana de 4
    # semanas (hoy, hoy+7, hoy+14, hoy+21).
    fechas = {sesion["fecha"] for sesion in cuerpo}
    esperadas = {(HOY + timedelta(days=7 * i)).isoformat() for i in range(4)}
    assert fechas == esperadas
    assert all(sesion["completada"] is False for sesion in cuerpo)
    assert all(sesion["rutina"]["id"] == rutina["id"] for sesion in cuerpo)
    assert all(sesion["rutina"]["nombre"] == "Push day" for sesion in cuerpo)


def test_calendario_no_crea_sesion_en_dias_sin_rutina_programada(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    # Solo se programa el día de hoy; el resto de la semana debe quedar vacío.
    _programar(client, headers, DIA_SEMANA_HOY, rutina["id"])

    cuerpo = _obtener_calendario(client, headers, HOY + timedelta(days=1), HOY + timedelta(days=6))

    assert cuerpo == []


def test_calendario_devuelve_solo_el_rango_pedido(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    _programar(client, headers, DIA_SEMANA_HOY, rutina["id"])

    # El relleno interno cubre las 4 semanas completas, pero solo se pide hoy.
    cuerpo = _obtener_calendario(client, headers, HOY, HOY)

    assert len(cuerpo) == 1
    assert cuerpo[0]["fecha"] == HOY.isoformat()


def test_calendario_no_incluye_sesiones_de_otro_usuario(client: TestClient) -> None:
    _, headers_1 = crear_usuario_autenticado(client)
    _, headers_2 = crear_usuario_autenticado(client)
    rutina_1 = _crear_rutina(client, headers_1)
    _programar(client, headers_1, DIA_SEMANA_HOY, rutina_1["id"])

    cuerpo = _obtener_calendario(client, headers_2, HOY, HOY + timedelta(days=27))

    assert cuerpo == []


def test_calendario_no_sobrescribe_sesion_modificada_manualmente(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    _programar(client, headers, DIA_SEMANA_HOY, rutina["id"])

    primera = _obtener_calendario(client, headers, HOY, HOY)
    assert len(primera) == 1
    sesion_id = primera[0]["id"]
    assert primera[0]["completada"] is False

    # Modificación manual: se finaliza la sesión de hoy.
    respuesta_finalizar = client.post(
        f"/api/v1/sesiones/{sesion_id}/finalizar", headers=headers
    )
    assert respuesta_finalizar.status_code == 200

    # Una segunda llamada al calendario (que vuelve a intentar rellenar
    # huecos) no debe crear una sesión duplicada para hoy ni resetear la que
    # ya se finalizó manualmente.
    segunda = _obtener_calendario(client, headers, HOY, HOY)

    assert len(segunda) == 1
    assert segunda[0]["id"] == sesion_id
    assert segunda[0]["completada"] is True


def test_calendario_no_duplica_sesiones_en_llamadas_repetidas(client: TestClient) -> None:
    _, headers = crear_usuario_autenticado(client)
    rutina = _crear_rutina(client, headers)
    _programar(client, headers, DIA_SEMANA_HOY, rutina["id"])

    _obtener_calendario(client, headers, HOY, HOY + timedelta(days=27))
    segunda = _obtener_calendario(client, headers, HOY, HOY + timedelta(days=27))

    fechas = [sesion["fecha"] for sesion in segunda]
    assert len(fechas) == len(set(fechas))
    assert len(fechas) == 4


def test_calendario_sin_token(client: TestClient) -> None:
    respuesta = client.get(
        f"/api/v1/calendario?desde={HOY.isoformat()}&hasta={HOY.isoformat()}"
    )

    assert respuesta.status_code == 401
