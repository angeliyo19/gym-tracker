from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Comida, PlanDia, RegistroAlimentacion, Usuario
from app.schemas import (
    RegistroAlimentacionCreate,
    RegistroAlimentacionRead,
    RegistroAlimentacionUpdate,
)

router = APIRouter(prefix="/registros-alimentacion", tags=["registros-alimentacion"])


def _get_registro_or_404(db: Session, registro_id: int) -> RegistroAlimentacion:
    registro = db.get(RegistroAlimentacion, registro_id)
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro de alimentación no encontrado"
        )
    return registro


def _validar_usuario(db: Session, usuario_id: int) -> None:
    if db.get(Usuario, usuario_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


def _validar_comida(db: Session, comida_id: int) -> None:
    if db.get(Comida, comida_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada")


def _validar_plan_dia(db: Session, plan_dia_id: int | None) -> None:
    if plan_dia_id is not None and db.get(PlanDia, plan_dia_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Día de plan no encontrado")


@router.post("/", response_model=RegistroAlimentacionRead, status_code=status.HTTP_201_CREATED)
def crear_registro(
    registro_in: RegistroAlimentacionCreate, db: Session = Depends(get_db)
) -> RegistroAlimentacion:
    _validar_usuario(db, registro_in.usuario_id)
    _validar_comida(db, registro_in.comida_id)
    _validar_plan_dia(db, registro_in.plan_dia_id)

    registro = RegistroAlimentacion(**registro_in.model_dump())
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


@router.get("/", response_model=list[RegistroAlimentacionRead])
def listar_registros(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[RegistroAlimentacion]:
    return db.query(RegistroAlimentacion).offset(skip).limit(limit).all()


@router.get("/{registro_id}", response_model=RegistroAlimentacionRead)
def obtener_registro(registro_id: int, db: Session = Depends(get_db)) -> RegistroAlimentacion:
    return _get_registro_or_404(db, registro_id)


@router.patch("/{registro_id}", response_model=RegistroAlimentacionRead)
def actualizar_registro(
    registro_id: int, registro_in: RegistroAlimentacionUpdate, db: Session = Depends(get_db)
) -> RegistroAlimentacion:
    registro = _get_registro_or_404(db, registro_id)

    datos = registro_in.model_dump(exclude_unset=True)
    if "comida_id" in datos:
        _validar_comida(db, datos["comida_id"])
    if "plan_dia_id" in datos:
        _validar_plan_dia(db, datos["plan_dia_id"])

    for campo, valor in datos.items():
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
