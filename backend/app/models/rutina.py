from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.rutina_ejercicio import RutinaEjercicio
    from app.models.sesion_entrenamiento import SesionEntrenamiento
    from app.models.usuario import Usuario


class Rutina(Base):
    __tablename__ = "rutinas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nombre: Mapped[str] = mapped_column(String(100))

    usuario: Mapped["Usuario"] = relationship(back_populates="rutinas")
    ejercicios: Mapped[list["RutinaEjercicio"]] = relationship(
        back_populates="rutina", passive_deletes="all"
    )
    sesiones: Mapped[list["SesionEntrenamiento"]] = relationship(
        back_populates="rutina", passive_deletes="all"
    )
