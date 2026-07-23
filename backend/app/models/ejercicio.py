from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ejercicio_grupo_muscular import EjercicioGrupoMuscular
    from app.models.serie import Serie


class Ejercicio(Base):
    __tablename__ = "ejercicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(20))

    grupos_musculares: Mapped[list["EjercicioGrupoMuscular"]] = relationship(back_populates="ejercicio")
    series: Mapped[list["Serie"]] = relationship(back_populates="ejercicio")
