from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.comida import Comida
    from app.models.plan_alimentacion import PlanAlimentacion
    from app.models.registro_alimentacion import RegistroAlimentacion


class PlanDia(Base):
    __tablename__ = "plan_dias"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("planes_alimentacion.id"))
    numero_dia: Mapped[int]
    franja: Mapped[str] = mapped_column(String(20))
    comida_id: Mapped[int] = mapped_column(ForeignKey("comidas.id"))
    orden: Mapped[int]

    plan: Mapped["PlanAlimentacion"] = relationship(back_populates="dias")
    comida: Mapped["Comida"] = relationship(back_populates="planes_dias")
    registros_alimentacion: Mapped[list["RegistroAlimentacion"]] = relationship(
        back_populates="plan_dia", passive_deletes="all"
    )
