from pydantic import BaseModel, ConfigDict

from app.schemas.ejercicio import EjercicioRead


class RutinaEjercicioInput(BaseModel):
    ejercicio_id: int
    orden: int
    series_objetivo: int
    repeticiones_objetivo: int


class RutinaEjercicioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ejercicio: EjercicioRead
    orden: int
    series_objetivo: int
    repeticiones_objetivo: int


class RutinaBase(BaseModel):
    nombre: str


class RutinaCreate(RutinaBase):
    usuario_id: int
    ejercicios: list[RutinaEjercicioInput] = []


class RutinaUpdate(BaseModel):
    nombre: str | None = None
    ejercicios: list[RutinaEjercicioInput] | None = None


class RutinaRead(RutinaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    ejercicios: list[RutinaEjercicioRead]
