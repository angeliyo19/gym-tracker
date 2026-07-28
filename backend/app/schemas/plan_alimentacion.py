from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.comida import ComidaRead

Franja = Literal["desayuno", "media_mañana", "almuerzo", "merienda", "cena"]


class PlanDiaInput(BaseModel):
    numero_dia: int
    franja: Franja
    comida_id: int
    orden: int


class PlanDiaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_dia: int
    franja: str
    orden: int
    comida: ComidaRead


class PlanAlimentacionBase(BaseModel):
    nombre: str


class PlanAlimentacionCreate(PlanAlimentacionBase):
    dias: list[PlanDiaInput] = []


class PlanAlimentacionUpdate(BaseModel):
    nombre: str | None = None
    dias: list[PlanDiaInput] | None = None


class PlanAlimentacionRead(PlanAlimentacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    dias: list[PlanDiaRead]
