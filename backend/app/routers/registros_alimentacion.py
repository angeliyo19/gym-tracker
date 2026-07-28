from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Comida, PlanAlimentacion, PlanDia, RegistroAlimentacion, Usuario
from app.schemas import (
    RegistroAlimentacionCreate,
    RegistroAlimentacionRead,
    RegistroAlimentacionUpdate,
)
from app.security import get_current_user

router = APIRouter(prefix="/registros-alimentacion", tags=["registros-alimentacion"])


def _get_registro_or_404(db: Session, registro_id: int, usuario_id: int) -> RegistroAlimentacion:
    registro = (
        db.query(RegistroAlimentacion)
        .filter(
            RegistroAlimentacion.id == registro_id,
            RegistroAlimentacion.usuario_id == usuario_id,
        )
        .first()
    )
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro de alimentación no encontrado"
        )
    return registro


def _validar_comida(db: Session, comida_id: int) -> None:
    if db.get(Comida, comida_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada")


def _validar_plan_dia(db: Session, plan_dia_id: int | None, usuario_id: int) -> None:
    if plan_dia_id is None:
        return
    plan_dia = (
        db.query(PlanDia)
        .join(PlanAlimentacion, PlanDia.plan_id == PlanAlimentacion.id)
        .filter(PlanDia.id == plan_dia_id, PlanAlimentacion.usuario_id == usuario_id)
        .first()
    )
    if plan_dia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Día de plan no encontrado")


@router.post("/", response_model=RegistroAlimentacionRead, status_code=status.HTTP_201_CREATED)
def crear_registro(
    registro_in: RegistroAlimentacionCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RegistroAlimentacion:
    _validar_comida(db, registro_in.comida_id)
    _validar_plan_dia(db, registro_in.plan_dia_id, usuario_actual.id)

    registro = RegistroAlimentacion(**registro_in.model_dump(), usuario_id=usuario_actual.id)
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
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RegistroAlimentacion]:
    return (
        db.query(RegistroAlimentacion)
        .filter(RegistroAlimentacion.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{registro_id}", response_model=RegistroAlimentacionRead)
def obtener_registro(
    registro_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RegistroAlimentacion:
    return _get_registro_or_404(db, registro_id, usuario_actual.id)


@router.patch("/{registro_id}", response_model=RegistroAlimentacionRead)
def actualizar_registro(
    registro_id: int,
    registro_in: RegistroAlimentacionUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RegistroAlimentacion:
    registro = _get_registro_or_404(db, registro_id, usuario_actual.id)

    datos = registro_in.model_dump(exclude_unset=True)
    if "comida_id" in datos:
        _validar_comida(db, datos["comida_id"])
    if "plan_dia_id" in datos:
        _validar_plan_dia(db, datos["plan_dia_id"], usuario_actual.id)

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
def eliminar_registro(
    registro_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    registro = _get_registro_or_404(db, registro_id, usuario_actual.id)
    db.delete(registro)
    db.commit()
