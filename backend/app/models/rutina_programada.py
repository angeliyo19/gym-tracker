from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.rutina import Rutina
    from app.models.usuario import Usuario


class RutinaProgramada(Base):
    __tablename__ = "rutinas_programadas"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "dia_semana", name="uq_rutina_programada_usuario_dia_semana"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    dia_semana: Mapped[str] = mapped_column(String(20))
    rutina_id: Mapped[int] = mapped_column(ForeignKey("rutinas.id"))

    usuario: Mapped["Usuario"] = relationship(back_populates="rutinas_programadas")
    rutina: Mapped["Rutina"] = relationship(back_populates="rutinas_programadas")
