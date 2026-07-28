from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RegistroEstadoAnimo, Usuario
from app.schemas import (
    RegistroEstadoAnimoCreate,
    RegistroEstadoAnimoRead,
    RegistroEstadoAnimoUpdate,
)

router = APIRouter(prefix="/registros-estado-animo", tags=["registros-estado-animo"])


def _get_registro_or_404(db: Session, registro_id: int) -> RegistroEstadoAnimo:
    registro = db.get(RegistroEstadoAnimo, registro_id)
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro de estado de ánimo no encontrado"
        )
    return registro


def _validar_usuario(db: Session, usuario_id: int) -> None:
    if db.get(Usuario, usuario_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


@router.post("/", response_model=RegistroEstadoAnimoRead, status_code=status.HTTP_201_CREATED)
def crear_registro(
    registro_in: RegistroEstadoAnimoCreate, db: Session = Depends(get_db)
) -> RegistroEstadoAnimo:
    _validar_usuario(db, registro_in.usuario_id)

    registro = RegistroEstadoAnimo(**registro_in.model_dump())
    db.add(registro)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear el registro (datos inválidos)",
        ) from exc
    db.refresh(registro)
    return registro


@router.get("/", response_model=list[RegistroEstadoAnimoRead])
def listar_registros(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[RegistroEstadoAnimo]:
    return db.query(RegistroEstadoAnimo).offset(skip).limit(limit).all()


@router.get("/{registro_id}", response_model=RegistroEstadoAnimoRead)
def obtener_registro(registro_id: int, db: Session = Depends(get_db)) -> RegistroEstadoAnimo:
    return _get_registro_or_404(db, registro_id)


@router.patch("/{registro_id}", response_model=RegistroEstadoAnimoRead)
def actualizar_registro(
    registro_id: int, registro_in: RegistroEstadoAnimoUpdate, db: Session = Depends(get_db)
) -> RegistroEstadoAnimo:
    registro = _get_registro_or_404(db, registro_id)
    for campo, valor in registro_in.model_dump(exclude_unset=True).items():
        setattr(registro, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar el registro (datos inválidos)",
        ) from exc
    db.refresh(registro)
    return registro


@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_registro(registro_id: int, db: Session = Depends(get_db)) -> None:
    registro = _get_registro_or_404(db, registro_id)
    db.delete(registro)
    db.commit()
