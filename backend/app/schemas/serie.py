from pydantic import BaseModel, ConfigDict


class SerieBase(BaseModel):
    ejercicio_id: int
    peso: float
    repeticiones: int
    rpe: float | None = None
    rir: float | None = None


class SerieCreate(SerieBase):
    pass


class SerieUpdate(BaseModel):
    ejercicio_id: int | None = None
    peso: float | None = None
    repeticiones: int | None = None
    rpe: float | None = None
    rir: float | None = None


class SerieRead(SerieBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sesion_id: int
