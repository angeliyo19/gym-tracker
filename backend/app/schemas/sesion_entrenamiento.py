from datetime import date

from pydantic import BaseModel, ConfigDict


class SesionEntrenamientoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    rutina_id: int
    fecha: date
    notas: str | None
