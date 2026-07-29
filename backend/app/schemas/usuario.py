from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    edad: int
    peso: float
    altura: float
    sexo: str
    objetivo: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    edad: int | None = None
    peso: float | None = None
    altura: float | None = None
    sexo: str | None = None
    objetivo: str | None = None


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    # Deliberadamente no está en UsuarioUpdate: el rol no debe poder
    # cambiarse desde PATCH /usuarios/me (un usuario no puede auto-asignarse
    # admin). Solo se expone en la lectura.
    rol: str
