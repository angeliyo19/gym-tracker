from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RegistroEstadoAnimo(Base):
    __tablename__ = "registros_estado_animo"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[date]
    valor: Mapped[int]
    notas: Mapped[str | None] = mapped_column(String(500))

    usuario: Mapped["Usuario"] = relationship(back_populates="registros_estado_animo")
