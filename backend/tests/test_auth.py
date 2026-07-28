from fastapi.testclient import TestClient

from tests.conftest import PASSWORD_POR_DEFECTO, auth_headers, obtener_token, registrar_usuario


def test_registro(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/auth/registro",
        json={
            "nombre": "Angel",
            "email": "nuevo@example.com",
            "edad": 25,
            "peso": 75.5,
            "altura": 1.78,
            "sexo": "masculino",
            "objetivo": "volumen",
            "password": PASSWORD_POR_DEFECTO,
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["email"] == "nuevo@example.com"
    assert "password" not in cuerpo
    assert "password_hash" not in cuerpo


def test_registro_email_duplicado(client: TestClient) -> None:
    usuario = registrar_usuario(client)

    respuesta = client.post(
        "/api/v1/auth/registro",
        json={
            "nombre": "Otro",
            "email": usuario["email"],
            "edad": 30,
            "peso": 80,
            "altura": 1.80,
            "sexo": "masculino",
            "objetivo": "definicion",
            "password": PASSWORD_POR_DEFECTO,
        },
    )

    assert respuesta.status_code == 409


def test_login_correcto(client: TestClient) -> None:
    usuario = registrar_usuario(client)

    respuesta = client.post(
        "/api/v1/auth/login",
        data={"username": usuario["email"], "password": PASSWORD_POR_DEFECTO},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert len(cuerpo["access_token"]) > 0


def test_login_password_incorrecta(client: TestClient) -> None:
    usuario = registrar_usuario(client)

    respuesta = client.post(
        "/api/v1/auth/login",
        data={"username": usuario["email"], "password": "password-equivocada"},
    )

    assert respuesta.status_code == 401


def test_login_email_inexistente(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/auth/login",
        data={"username": "no-existe@example.com", "password": PASSWORD_POR_DEFECTO},
    )

    assert respuesta.status_code == 401


def test_acceso_sin_token(client: TestClient) -> None:
    respuesta = client.get("/api/v1/usuarios/me")

    assert respuesta.status_code == 401


def test_acceso_token_invalido(client: TestClient) -> None:
    respuesta = client.get("/api/v1/usuarios/me", headers=auth_headers("token-invalido"))

    assert respuesta.status_code == 401


def test_acceso_con_token_valido(client: TestClient) -> None:
    usuario = registrar_usuario(client)
    token = obtener_token(client, usuario["email"])

    respuesta = client.get("/api/v1/usuarios/me", headers=auth_headers(token))

    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == usuario["email"]
