from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.plan_dia import PlanDia
    from app.models.usuario import Usuario


class PlanAlimentacion(Base):
    __tablename__ = "planes_alimentacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nombre: Mapped[str] = mapped_column(String(100))

    usuario: Mapped["Usuario"] = relationship(back_populates="planes_alimentacion")
    dias: Mapped[list["PlanDia"]] = relationship(back_populates="plan", passive_deletes="all")
