from pydantic import BaseModel, ConfigDict

from app.schemas.grupo_muscular import GrupoMuscularRead


class EjercicioGrupoMuscularInput(BaseModel):
    grupo_muscular_id: int
    es_principal: bool = False


class EjercicioGrupoMuscularRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    grupo_muscular: GrupoMuscularRead
    es_principal: bool


class EjercicioBase(BaseModel):
    nombre: str
    tipo: str


class EjercicioCreate(EjercicioBase):
    grupos_musculares: list[EjercicioGrupoMuscularInput] = []


class EjercicioUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    grupos_musculares: list[EjercicioGrupoMuscularInput] | None = None


class EjercicioRead(EjercicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    grupos_musculares: list[EjercicioGrupoMuscularRead]
