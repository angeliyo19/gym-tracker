from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class RegistroEstadoAnimoBase(BaseModel):
    fecha: date
    valor: int = Field(ge=1, le=5)
    notas: str | None = None


class RegistroEstadoAnimoCreate(RegistroEstadoAnimoBase):
    usuario_id: int


class RegistroEstadoAnimoUpdate(BaseModel):
    fecha: date | None = None
    valor: int | None = Field(default=None, ge=1, le=5)
    notas: str | None = None


class RegistroEstadoAnimoRead(RegistroEstadoAnimoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
