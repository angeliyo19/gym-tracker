from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Serie, SesionEntrenamiento, Usuario
from app.routers.rutinas import _get_rutina_or_404, construir_ultimas_series
from app.schemas import (
    RutinaRead,
    SeriesPorEjercicio,
    SesionDetalleRead,
    SesionEntrenamientoRead,
    SesionEntrenamientoUpdate,
)
from app.security import get_current_user

router = APIRouter(prefix="/sesiones", tags=["sesiones"])


def _get_sesion_or_404(db: Session, sesion_id: int, usuario_id: int) -> SesionEntrenamiento:
    sesion = (
        db.query(SesionEntrenamiento)
        .filter(SesionEntrenamiento.id == sesion_id, SesionEntrenamiento.usuario_id == usuario_id)
        .first()
    )
    if sesion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión de entrenamiento no encontrada"
        )
    return sesion


def _agrupar_series_por_ejercicio(series: list[Serie]) -> list[SeriesPorEjercicio]:
    agrupadas: dict[int, list[Serie]] = {}
    for serie in series:
        agrupadas.setdefault(serie.ejercicio_id, []).append(serie)
    return [
        SeriesPorEjercicio(ejercicio_id=ejercicio_id, series=series_del_ejercicio)
        for ejercicio_id, series_del_ejercicio in agrupadas.items()
    ]


@router.get("/", response_model=list[SesionEntrenamientoRead])
def listar_sesiones(
    rutina_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SesionEntrenamiento]:
    query = db.query(SesionEntrenamiento).filter(SesionEntrenamiento.usuario_id == usuario_actual.id)
    if rutina_id is not None:
        query = query.filter(SesionEntrenamiento.rutina_id == rutina_id)
    return (
        query.order_by(SesionEntrenamiento.fecha.desc(), SesionEntrenamiento.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{sesion_id}", response_model=SesionDetalleRead)
def obtener_sesion(
    sesion_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SesionDetalleRead:
    sesion = _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    rutina = _get_rutina_or_404(db, sesion.rutina_id, usuario_actual.id)

    ejercicio_ids = {asociacion.ejercicio_id for asociacion in rutina.ejercicios}
    ultimas_series = construir_ultimas_series(db, usuario_actual.id, ejercicio_ids)

    series = db.query(Serie).filter(Serie.sesion_id == sesion.id).order_by(Serie.id).all()
    series_registradas = _agrupar_series_por_ejercicio(series)

    return SesionDetalleRead(
        id=sesion.id,
        usuario_id=sesion.usuario_id,
        rutina_id=sesion.rutina_id,
        fecha=sesion.fecha,
        notas=sesion.notas,
        completada=sesion.completada,
        rutina=RutinaRead.model_validate(rutina),
        ultimas_series=ultimas_series,
        series_registradas=series_registradas,
    )


@router.patch("/{sesion_id}", response_model=SesionEntrenamientoRead)
def actualizar_sesion(
    sesion_id: int,
    sesion_in: SesionEntrenamientoUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SesionEntrenamiento:
    """Cambia la fecha y/o la rutina de una sesión concreta (ej. desde el
    calendario), sin afectar al patrón semanal de RutinaProgramada que la
    generó. Solo se permite mientras la sesión no se haya finalizado."""
    sesion = _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    if sesion.completada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede modificar una sesión ya completada",
        )

    datos = sesion_in.model_dump(exclude_unset=True)
    if "rutina_id" in datos:
        _get_rutina_or_404(db, datos["rutina_id"], usuario_actual.id)
    for campo, valor in datos.items():
        setattr(sesion, campo, valor)

    db.commit()
    db.refresh(sesion)
    return sesion


@router.post("/{sesion_id}/finalizar", response_model=SesionEntrenamientoRead)
def finalizar_sesion(
    sesion_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SesionEntrenamiento:
    """Marca la sesión como completada. Idempotente: si ya lo estaba, no es un error."""
    sesion = _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    sesion.completada = True
    db.commit()
    db.refresh(sesion)
    return sesion
