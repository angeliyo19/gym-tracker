from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class RegistroPesoBase(BaseModel):
    fecha: date
    peso: float
    porcentaje_grasa: float | None = None
    masa_muscular_kg: float | None = None
    detalle_medidas: dict[str, Any] | None = None


class RegistroPesoCreate(RegistroPesoBase):
    pass


class RegistroPesoUpdate(BaseModel):
    fecha: date | None = None
    peso: float | None = None
    porcentaje_grasa: float | None = None
    masa_muscular_kg: float | None = None
    detalle_medidas: dict[str, Any] | None = None


class RegistroPesoRead(RegistroPesoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
