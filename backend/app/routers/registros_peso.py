from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RegistroPeso, Usuario
from app.schemas import RegistroPesoCreate, RegistroPesoRead, RegistroPesoUpdate
from app.security import get_current_user

router = APIRouter(prefix="/registros-peso", tags=["registros-peso"])


def _get_registro_or_404(db: Session, registro_id: int, usuario_id: int) -> RegistroPeso:
    registro = (
        db.query(RegistroPeso)
        .filter(RegistroPeso.id == registro_id, RegistroPeso.usuario_id == usuario_id)
        .first()
    )
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro de peso no encontrado"
        )
    return registro


@router.post("/", response_model=RegistroPesoRead, status_code=status.HTTP_201_CREATED)
def crear_registro(
    registro_in: RegistroPesoCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RegistroPeso:
    registro = RegistroPeso(**registro_in.model_dump(), usuario_id=usuario_actual.id)
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


@router.get("/", response_model=list[RegistroPesoRead])
def listar_registros(
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RegistroPeso]:
    return (
        db.query(RegistroPeso)
        .filter(RegistroPeso.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{registro_id}", response_model=RegistroPesoRead)
def obtener_registro(
    registro_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RegistroPeso:
    return _get_registro_or_404(db, registro_id, usuario_actual.id)


@router.patch("/{registro_id}", response_model=RegistroPesoRead)
def actualizar_registro(
    registro_id: int,
    registro_in: RegistroPesoUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RegistroPeso:
    registro = _get_registro_or_404(db, registro_id, usuario_actual.id)
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
def eliminar_registro(
    registro_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    registro = _get_registro_or_404(db, registro_id, usuario_actual.id)
    db.delete(registro)
    db.commit()
