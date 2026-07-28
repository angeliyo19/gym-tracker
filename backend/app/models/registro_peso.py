from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RegistroPeso(Base):
    __tablename__ = "registros_peso"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[date]
    peso: Mapped[float]
    porcentaje_grasa: Mapped[float | None]

    usuario: Mapped["Usuario"] = relationship(back_populates="registros_peso")
