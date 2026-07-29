from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import RutinaProgramada, SesionEntrenamiento, Usuario
from app.schemas import SesionCalendarioRead
from app.schemas.rutina_programada import DIAS_SEMANA
from app.security import get_current_user

router = APIRouter(prefix="/calendario", tags=["calendario"])

DIAS_A_RELLENAR = 28  # las próximas 4 semanas, incluyendo hoy


def _dia_semana(fecha: date) -> str:
    return DIAS_SEMANA[fecha.weekday()]


def _rellenar_huecos(db: Session, usuario_id: int) -> None:
    """Crea sesiones pendientes (completada=False) en las próximas 4 semanas
    para cada fecha sin ninguna sesión ya registrada, según lo que indique
    RutinaProgramada para ese día de la semana. Nunca toca una fecha que ya
    tenga una sesión (auto-generada o creada/editada a mano)."""
    hoy = date.today()
    ultimo_dia = hoy + timedelta(days=DIAS_A_RELLENAR - 1)

    rutina_por_dia = {
        programada.dia_semana: programada.rutina_id
        for programada in db.query(RutinaProgramada)
        .filter(RutinaProgramada.usuario_id == usuario_id)
        .all()
    }
    if not rutina_por_dia:
        return

    fechas_con_sesion = {
        fecha
        for (fecha,) in db.query(SesionEntrenamiento.fecha)
        .filter(
            SesionEntrenamiento.usuario_id == usuario_id,
            SesionEntrenamiento.fecha >= hoy,
            SesionEntrenamiento.fecha <= ultimo_dia,
        )
        .all()
    }

    fecha = hoy
    while fecha <= ultimo_dia:
        if fecha not in fechas_con_sesion:
            rutina_id = rutina_por_dia.get(_dia_semana(fecha))
            if rutina_id is not None:
                db.add(
                    SesionEntrenamiento(
                        usuario_id=usuario_id, rutina_id=rutina_id, fecha=fecha, completada=False
                    )
                )
        fecha += timedelta(days=1)

    db.commit()


@router.get("", response_model=list[SesionCalendarioRead])
def obtener_calendario(
    desde: date,
    hasta: date,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SesionEntrenamiento]:
    _rellenar_huecos(db, usuario_actual.id)

    return (
        db.query(SesionEntrenamiento)
        .options(selectinload(SesionEntrenamiento.rutina))
        .filter(
            SesionEntrenamiento.usuario_id == usuario_actual.id,
            SesionEntrenamiento.fecha >= desde,
            SesionEntrenamiento.fecha <= hasta,
        )
        .order_by(SesionEntrenamiento.fecha)
        .all()
    )
