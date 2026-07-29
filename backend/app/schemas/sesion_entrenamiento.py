from datetime import date

from pydantic import BaseModel, ConfigDict

from app.schemas.rutina import RutinaRead
from app.schemas.serie import SerieRead


class SesionEntrenamientoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    rutina_id: int
    fecha: date
    notas: str | None
    completada: bool


class UltimaSerieRef(BaseModel):
    ejercicio_id: int
    peso: float
    repeticiones: int
    fecha: date


class IniciarRutinaRead(SesionEntrenamientoRead):
    ultimas_series: list[UltimaSerieRef]


class SeriesPorEjercicio(BaseModel):
    ejercicio_id: int
    series: list[SerieRead]


class SesionDetalleRead(SesionEntrenamientoRead):
    rutina: RutinaRead
    ultimas_series: list[UltimaSerieRef]
    series_registradas: list[SeriesPorEjercicio]
