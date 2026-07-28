from pydantic import BaseModel, ConfigDict


class ComidaBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    calorias: float | None = None


class ComidaCreate(ComidaBase):
    pass


class ComidaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    calorias: float | None = None


class ComidaRead(ComidaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
