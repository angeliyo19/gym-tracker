from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Comida, Usuario
from app.schemas import ComidaCreate, ComidaRead, ComidaUpdate
from app.security import get_current_user

router = APIRouter(prefix="/comidas", tags=["comidas"])


def _get_comida_or_404(db: Session, comida_id: int, usuario_id: int) -> Comida:
    comida = (
        db.query(Comida)
        .filter(Comida.id == comida_id, Comida.usuario_id == usuario_id)
        .first()
    )
    if comida is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada")
    return comida


@router.post("/", response_model=ComidaRead, status_code=status.HTTP_201_CREATED)
def crear_comida(
    comida_in: ComidaCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Comida:
    comida = Comida(**comida_in.model_dump(), usuario_id=usuario_actual.id)
    db.add(comida)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear la comida (datos inválidos)",
        ) from exc
    db.refresh(comida)
    return comida


@router.get("/", response_model=list[ComidaRead])
def listar_comidas(
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Comida]:
    return (
        db.query(Comida)
        .filter(Comida.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{comida_id}", response_model=ComidaRead)
def obtener_comida(
    comida_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Comida:
    return _get_comida_or_404(db, comida_id, usuario_actual.id)


@router.patch("/{comida_id}", response_model=ComidaRead)
def actualizar_comida(
    comida_id: int,
    comida_in: ComidaUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Comida:
    comida = _get_comida_or_404(db, comida_id, usuario_actual.id)
    for campo, valor in comida_in.model_dump(exclude_unset=True).items():
        setattr(comida, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar la comida (datos inválidos)",
        ) from exc
    db.refresh(comida)
    return comida


@router.delete("/{comida_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_comida(
    comida_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    comida = _get_comida_or_404(db, comida_id, usuario_actual.id)
    db.delete(comida)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la comida está en uso en algún plan o registro",
        ) from exc
