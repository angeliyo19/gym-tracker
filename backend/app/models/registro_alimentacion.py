from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.comida import Comida
    from app.models.plan_dia import PlanDia
    from app.models.usuario import Usuario


class RegistroAlimentacion(Base):
    __tablename__ = "registros_alimentacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[date]
    plan_dia_id: Mapped[int | None] = mapped_column(ForeignKey("plan_dias.id"))
    comida_id: Mapped[int] = mapped_column(ForeignKey("comidas.id"))
    completada: Mapped[bool] = mapped_column(Boolean, default=False)
    calorias: Mapped[float]

    usuario: Mapped["Usuario"] = relationship(back_populates="registros_alimentacion")
    plan_dia: Mapped[Optional["PlanDia"]] = relationship(
        back_populates="registros_alimentacion"
    )
    comida: Mapped["Comida"] = relationship(back_populates="registros_alimentacion")
