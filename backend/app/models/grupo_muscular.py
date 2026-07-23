from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ejercicio_grupo_muscular import EjercicioGrupoMuscular


class GrupoMuscular(Base):
    __tablename__ = "grupos_musculares"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)

    ejercicios: Mapped[list["EjercicioGrupoMuscular"]] = relationship(back_populates="grupo_muscular")
