from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Comida, Usuario
from app.schemas import ComidaCreate, ComidaRead, ComidaUpdate

router = APIRouter(prefix="/comidas", tags=["comidas"])


def _get_comida_or_404(db: Session, comida_id: int) -> Comida:
    comida = db.get(Comida, comida_id)
    if comida is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada")
    return comida


def _validar_usuario(db: Session, usuario_id: int) -> None:
    if db.get(Usuario, usuario_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


@router.post("/", response_model=ComidaRead, status_code=status.HTTP_201_CREATED)
def crear_comida(comida_in: ComidaCreate, db: Session = Depends(get_db)) -> Comida:
    _validar_usuario(db, comida_in.usuario_id)

    comida = Comida(**comida_in.model_dump())
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
def listar_comidas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[Comida]:
    return db.query(Comida).offset(skip).limit(limit).all()


@router.get("/{comida_id}", response_model=ComidaRead)
def obtener_comida(comida_id: int, db: Session = Depends(get_db)) -> Comida:
    return _get_comida_or_404(db, comida_id)


@router.patch("/{comida_id}", response_model=ComidaRead)
def actualizar_comida(
    comida_id: int, comida_in: ComidaUpdate, db: Session = Depends(get_db)
) -> Comida:
    comida = _get_comida_or_404(db, comida_id)
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
def eliminar_comida(comida_id: int, db: Session = Depends(get_db)) -> None:
    comida = _get_comida_or_404(db, comida_id)
    db.delete(comida)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la comida está en uso en algún plan o registro",
        ) from exc
