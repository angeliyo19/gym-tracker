from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.sesion_entrenamiento import SesionEntrenamiento


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    edad: Mapped[int]
    peso: Mapped[float]
    altura: Mapped[float]
    sexo: Mapped[str] = mapped_column(String(20))
    objetivo: Mapped[str] = mapped_column(String(20))

    sesiones: Mapped[list["SesionEntrenamiento"]] = relationship(back_populates="usuario")
