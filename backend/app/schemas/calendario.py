from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class RutinaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class SesionCalendarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    completada: bool
    hora_inicio: datetime | None
    hora_fin: datetime | None
    rutina: RutinaResumen
