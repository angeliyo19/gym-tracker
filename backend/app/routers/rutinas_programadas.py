from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Rutina, RutinaProgramada, Usuario
from app.schemas import RutinaProgramadaCreate, RutinaProgramadaRead, RutinaProgramadaUpdate
from app.security import get_current_user

router = APIRouter(prefix="/rutinas-programadas", tags=["rutinas-programadas"])


def _get_programada_or_404(db: Session, programada_id: int, usuario_id: int) -> RutinaProgramada:
    programada = (
        db.query(RutinaProgramada)
        .filter(RutinaProgramada.id == programada_id, RutinaProgramada.usuario_id == usuario_id)
        .first()
    )
    if programada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rutina programada no encontrada"
        )
    return programada


def _validar_rutina(db: Session, rutina_id: int, usuario_id: int) -> None:
    existe = (
        db.query(Rutina.id).filter(Rutina.id == rutina_id, Rutina.usuario_id == usuario_id).first()
    )
    if existe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")


@router.post("/", response_model=RutinaProgramadaRead, status_code=status.HTTP_201_CREATED)
def crear_rutina_programada(
    programada_in: RutinaProgramadaCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RutinaProgramada:
    _validar_rutina(db, programada_in.rutina_id, usuario_actual.id)

    programada = RutinaProgramada(**programada_in.model_dump(), usuario_id=usuario_actual.id)
    db.add(programada)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una rutina programada para ese día de la semana",
        ) from exc
    db.refresh(programada)
    return programada


@router.get("/", response_model=list[RutinaProgramadaRead])
def listar_rutinas_programadas(
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RutinaProgramada]:
    return (
        db.query(RutinaProgramada)
        .filter(RutinaProgramada.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{programada_id}", response_model=RutinaProgramadaRead)
def obtener_rutina_programada(
    programada_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RutinaProgramada:
    return _get_programada_or_404(db, programada_id, usuario_actual.id)


@router.patch("/{programada_id}", response_model=RutinaProgramadaRead)
def actualizar_rutina_programada(
    programada_id: int,
    programada_in: RutinaProgramadaUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RutinaProgramada:
    programada = _get_programada_or_404(db, programada_id, usuario_actual.id)

    datos = programada_in.model_dump(exclude_unset=True)
    if "rutina_id" in datos:
        _validar_rutina(db, datos["rutina_id"], usuario_actual.id)
    for campo, valor in datos.items():
        setattr(programada, campo, valor)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una rutina programada para ese día de la semana",
        ) from exc
    db.refresh(programada)
    return programada


@router.delete("/{programada_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rutina_programada(
    programada_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    programada = _get_programada_or_404(db, programada_id, usuario_actual.id)
    db.delete(programada)
    db.commit()
