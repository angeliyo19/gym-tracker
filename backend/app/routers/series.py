from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Ejercicio, SesionEntrenamiento, Serie, Usuario
from app.schemas import SerieCreate, SerieRead, SerieUpdate
from app.security import get_current_user

router = APIRouter(prefix="/sesiones/{sesion_id}/series", tags=["series"])


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


def _validar_ejercicio(db: Session, ejercicio_id: int) -> None:
    if db.get(Ejercicio, ejercicio_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado")


def _get_serie_or_404(db: Session, sesion_id: int, serie_id: int) -> Serie:
    serie = (
        db.query(Serie)
        .filter(Serie.id == serie_id, Serie.sesion_id == sesion_id)
        .first()
    )
    if serie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serie no encontrada")
    return serie


@router.post("/", response_model=SerieRead, status_code=status.HTTP_201_CREATED)
def crear_serie(
    sesion_id: int,
    serie_in: SerieCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Serie:
    sesion = _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    _validar_ejercicio(db, serie_in.ejercicio_id)

    if sesion.hora_inicio is None:
        sesion.hora_inicio = datetime.now(timezone.utc)

    serie = Serie(sesion_id=sesion_id, **serie_in.model_dump())
    db.add(serie)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear la serie (datos inválidos)",
        ) from exc
    db.refresh(serie)
    return serie


@router.get("/", response_model=list[SerieRead])
def listar_series(
    sesion_id: int,
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Serie]:
    _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    return (
        db.query(Serie)
        .filter(Serie.sesion_id == sesion_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{serie_id}", response_model=SerieRead)
def obtener_serie(
    sesion_id: int,
    serie_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Serie:
    _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    return _get_serie_or_404(db, sesion_id, serie_id)


@router.patch("/{serie_id}", response_model=SerieRead)
def actualizar_serie(
    sesion_id: int,
    serie_id: int,
    serie_in: SerieUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Serie:
    _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    serie = _get_serie_or_404(db, sesion_id, serie_id)

    datos = serie_in.model_dump(exclude_unset=True)
    if "ejercicio_id" in datos:
        _validar_ejercicio(db, datos["ejercicio_id"])
    for campo, valor in datos.items():
        setattr(serie, campo, valor)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar la serie (datos inválidos)",
        ) from exc
    db.refresh(serie)
    return serie


@router.delete("/{serie_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_serie(
    sesion_id: int,
    serie_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    serie = _get_serie_or_404(db, sesion_id, serie_id)
    db.delete(serie)
    db.commit()
