from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ejercicio import Ejercicio
    from app.models.sesion_entrenamiento import SesionEntrenamiento


class Serie(Base):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(primary_key=True)
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesiones_entrenamiento.id"))
    ejercicio_id: Mapped[int] = mapped_column(ForeignKey("ejercicios.id"))
    peso: Mapped[float]
    repeticiones: Mapped[int]
    rpe: Mapped[float | None]
    rir: Mapped[float | None]

    sesion: Mapped["SesionEntrenamiento"] = relationship(back_populates="series")
    ejercicio: Mapped["Ejercicio"] = relationship(back_populates="series")
