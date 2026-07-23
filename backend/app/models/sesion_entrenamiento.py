from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.serie import Serie
    from app.models.usuario import Usuario


class SesionEntrenamiento(Base):
    __tablename__ = "sesiones_entrenamiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[date]
    notas: Mapped[str | None] = mapped_column(String(500))

    usuario: Mapped["Usuario"] = relationship(back_populates="sesiones")
    series: Mapped[list["Serie"]] = relationship(back_populates="sesion")
