from pydantic import BaseModel

from app.schemas.usuario import UsuarioBase


class UsuarioRegistro(UsuarioBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
