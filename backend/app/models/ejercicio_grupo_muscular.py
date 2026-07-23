from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ejercicio import Ejercicio
    from app.models.grupo_muscular import GrupoMuscular


class EjercicioGrupoMuscular(Base):
    __tablename__ = "ejercicios_grupos_musculares"

    ejercicio_id: Mapped[int] = mapped_column(ForeignKey("ejercicios.id"), primary_key=True)
    grupo_muscular_id: Mapped[int] = mapped_column(ForeignKey("grupos_musculares.id"), primary_key=True)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False)

    ejercicio: Mapped["Ejercicio"] = relationship(back_populates="grupos_musculares")
    grupo_muscular: Mapped["GrupoMuscular"] = relationship(back_populates="ejercicios")
