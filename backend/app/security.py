from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Usuario

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CREDENCIALES_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar la credencial",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def crear_access_token(usuario_id: int) -> str:
    """Genera un JWT de acceso para el usuario, con la expiración configurada."""
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """Dependencia de FastAPI: valida el JWT del header Authorization y devuelve el Usuario."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise _CREDENCIALES_INVALIDAS from exc

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise _CREDENCIALES_INVALIDAS

    usuario = db.get(Usuario, int(usuario_id))
    if usuario is None:
        raise _CREDENCIALES_INVALIDAS
    return usuario


def require_admin(usuario_actual: Usuario = Depends(get_current_user)) -> Usuario:
    """Dependencia de FastAPI: exige que el usuario autenticado tenga rol admin."""
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return usuario_actual
