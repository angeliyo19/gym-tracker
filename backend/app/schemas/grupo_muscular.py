from pydantic import BaseModel, ConfigDict


class GrupoMuscularBase(BaseModel):
    nombre: str


class GrupoMuscularCreate(GrupoMuscularBase):
    pass


class GrupoMuscularUpdate(BaseModel):
    nombre: str | None = None


class GrupoMuscularRead(GrupoMuscularBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
