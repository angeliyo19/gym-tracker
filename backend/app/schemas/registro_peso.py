from datetime import date

from pydantic import BaseModel, ConfigDict


class RegistroPesoBase(BaseModel):
    fecha: date
    peso: float
    porcentaje_grasa: float | None = None


class RegistroPesoCreate(RegistroPesoBase):
    usuario_id: int


class RegistroPesoUpdate(BaseModel):
    fecha: date | None = None
    peso: float | None = None
    porcentaje_grasa: float | None = None


class RegistroPesoRead(RegistroPesoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
