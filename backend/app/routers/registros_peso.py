from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RegistroPeso, Usuario
from app.schemas import RegistroPesoCreate, RegistroPesoRead, RegistroPesoUpdate

router = APIRouter(prefix="/registros-peso", tags=["registros-peso"])


def _get_registro_or_404(db: Session, registro_id: int) -> RegistroPeso:
    registro = db.get(RegistroPeso, registro_id)
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro de peso no encontrado"
        )
    return registro


def _validar_usuario(db: Session, usuario_id: int) -> None:
    if db.get(Usuario, usuario_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


@router.post("/", response_model=RegistroPesoRead, status_code=status.HTTP_201_CREATED)
def crear_registro(registro_in: RegistroPesoCreate, db: Session = Depends(get_db)) -> RegistroPeso:
    _validar_usuario(db, registro_in.usuario_id)

    registro = RegistroPeso(**registro_in.model_dump())
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
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[RegistroPeso]:
    return db.query(RegistroPeso).offset(skip).limit(limit).all()


@router.get("/{registro_id}", response_model=RegistroPesoRead)
def obtener_registro(registro_id: int, db: Session = Depends(get_db)) -> RegistroPeso:
    return _get_registro_or_404(db, registro_id)


@router.patch("/{registro_id}", response_model=RegistroPesoRead)
def actualizar_registro(
    registro_id: int, registro_in: RegistroPesoUpdate, db: Session = Depends(get_db)
) -> RegistroPeso:
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
