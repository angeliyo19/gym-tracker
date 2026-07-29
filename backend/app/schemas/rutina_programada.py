from typing import Literal

from pydantic import BaseModel, ConfigDict

DIAS_SEMANA: tuple[str, ...] = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)

DiaSemana = Literal["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


class RutinaProgramadaBase(BaseModel):
    dia_semana: DiaSemana
    rutina_id: int


class RutinaProgramadaCreate(RutinaProgramadaBase):
    pass


class RutinaProgramadaUpdate(BaseModel):
    dia_semana: DiaSemana | None = None
    rutina_id: int | None = None


class RutinaProgramadaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    dia_semana: str
    rutina_id: int
