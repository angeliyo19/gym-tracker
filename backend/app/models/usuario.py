from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.comida import Comida
    from app.models.plan_alimentacion import PlanAlimentacion
    from app.models.registro_alimentacion import RegistroAlimentacion
    from app.models.registro_estado_animo import RegistroEstadoAnimo
    from app.models.registro_peso import RegistroPeso
    from app.models.rutina import Rutina
    from app.models.rutina_programada import RutinaProgramada
    from app.models.sesion_entrenamiento import SesionEntrenamiento


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    edad: Mapped[int]
    peso: Mapped[float]
    altura: Mapped[float]
    sexo: Mapped[str] = mapped_column(String(20))
    objetivo: Mapped[str] = mapped_column(String(20))

    sesiones: Mapped[list["SesionEntrenamiento"]] = relationship(back_populates="usuario")
    rutinas: Mapped[list["Rutina"]] = relationship(back_populates="usuario", passive_deletes="all")
    comidas: Mapped[list["Comida"]] = relationship(back_populates="usuario", passive_deletes="all")
    planes_alimentacion: Mapped[list["PlanAlimentacion"]] = relationship(
        back_populates="usuario", passive_deletes="all"
    )
    registros_alimentacion: Mapped[list["RegistroAlimentacion"]] = relationship(
        back_populates="usuario", passive_deletes="all"
    )
    registros_peso: Mapped[list["RegistroPeso"]] = relationship(
        back_populates="usuario", passive_deletes="all"
    )
    registros_estado_animo: Mapped[list["RegistroEstadoAnimo"]] = relationship(
        back_populates="usuario", passive_deletes="all"
    )
    rutinas_programadas: Mapped[list["RutinaProgramada"]] = relationship(
        back_populates="usuario", passive_deletes="all"
    )
