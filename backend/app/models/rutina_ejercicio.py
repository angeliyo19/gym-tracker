from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ejercicio import Ejercicio
    from app.models.rutina import Rutina


class RutinaEjercicio(Base):
    __tablename__ = "rutina_ejercicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    rutina_id: Mapped[int] = mapped_column(ForeignKey("rutinas.id"))
    ejercicio_id: Mapped[int] = mapped_column(ForeignKey("ejercicios.id"))
    orden: Mapped[int]
    series_objetivo: Mapped[int]
    repeticiones_objetivo: Mapped[int]

    rutina: Mapped["Rutina"] = relationship(back_populates="ejercicios")
    ejercicio: Mapped["Ejercicio"] = relationship(back_populates="rutina_ejercicios")
