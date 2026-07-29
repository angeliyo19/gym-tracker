from datetime import date, datetime

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
    hora_inicio: datetime | None
    hora_fin: datetime | None


class SesionEntrenamientoUpdate(BaseModel):
    fecha: date | None = None
    rutina_id: int | None = None


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
