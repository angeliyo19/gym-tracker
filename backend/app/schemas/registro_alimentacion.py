from datetime import date

from pydantic import BaseModel, ConfigDict


class RegistroAlimentacionBase(BaseModel):
    fecha: date
    comida_id: int
    plan_dia_id: int | None = None
    completada: bool = False
    calorias: float


class RegistroAlimentacionCreate(RegistroAlimentacionBase):
    usuario_id: int


class RegistroAlimentacionUpdate(BaseModel):
    fecha: date | None = None
    comida_id: int | None = None
    plan_dia_id: int | None = None
    completada: bool | None = None
    calorias: float | None = None


class RegistroAlimentacionRead(RegistroAlimentacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
