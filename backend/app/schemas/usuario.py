from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    edad: int
    peso: float
    altura: float
    sexo: str
    objetivo: str


class UsuarioCreate(UsuarioBase):
    pass


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
