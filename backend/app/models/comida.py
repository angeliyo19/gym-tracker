from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.plan_dia import PlanDia
    from app.models.registro_alimentacion import RegistroAlimentacion
    from app.models.usuario import Usuario


class Comida(Base):
    __tablename__ = "comidas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    calorias: Mapped[float | None]

    usuario: Mapped["Usuario"] = relationship(back_populates="comidas")
    planes_dias: Mapped[list["PlanDia"]] = relationship(
        back_populates="comida", passive_deletes="all"
    )
    registros_alimentacion: Mapped[list["RegistroAlimentacion"]] = relationship(
        back_populates="comida", passive_deletes="all"
    )
