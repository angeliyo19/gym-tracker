from pydantic import BaseModel, ConfigDict


class ComidaBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    calorias: float | None = None


class ComidaCreate(ComidaBase):
    usuario_id: int


class ComidaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    calorias: float | None = None


class ComidaRead(ComidaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
