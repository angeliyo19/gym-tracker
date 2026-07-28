from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Comida, PlanAlimentacion, PlanDia, Usuario
from app.schemas import (
    PlanAlimentacionCreate,
    PlanAlimentacionRead,
    PlanAlimentacionUpdate,
    PlanDiaInput,
)
from app.security import get_current_user

router = APIRouter(prefix="/planes-alimentacion", tags=["planes-alimentacion"])

_CARGA_DIAS = selectinload(PlanAlimentacion.dias).selectinload(PlanDia.comida)


def _get_plan_or_404(db: Session, plan_id: int, usuario_id: int) -> PlanAlimentacion:
    plan = (
        db.query(PlanAlimentacion)
        .options(_CARGA_DIAS)
        .filter(PlanAlimentacion.id == plan_id, PlanAlimentacion.usuario_id == usuario_id)
        .first()
    )
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plan de alimentación no encontrado"
        )
    return plan


def _validar_comidas(db: Session, dias: list[PlanDiaInput]) -> None:
    ids = {dia.comida_id for dia in dias}
    if not ids:
        return
    encontrados = {id_ for (id_,) in db.query(Comida.id).filter(Comida.id.in_(ids)).all()}
    faltantes = ids - encontrados
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comida(s) no encontrada(s): {sorted(faltantes)}",
        )


def _reemplazar_dias(db: Session, plan_id: int, dias: list[PlanDiaInput]) -> None:
    db.query(PlanDia).filter(PlanDia.plan_id == plan_id).delete()
    for dia in dias:
        db.add(
            PlanDia(
                plan_id=plan_id,
                numero_dia=dia.numero_dia,
                franja=dia.franja,
                comida_id=dia.comida_id,
                orden=dia.orden,
            )
        )


@router.post("/", response_model=PlanAlimentacionRead, status_code=status.HTTP_201_CREATED)
def crear_plan(
    plan_in: PlanAlimentacionCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanAlimentacion:
    _validar_comidas(db, plan_in.dias)

    plan = PlanAlimentacion(usuario_id=usuario_actual.id, nombre=plan_in.nombre)
    db.add(plan)
    db.flush()
    _reemplazar_dias(db, plan.id, plan_in.dias)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear el plan de alimentación (datos duplicados o inválidos)",
        ) from exc

    return _get_plan_or_404(db, plan.id, usuario_actual.id)


@router.get("/", response_model=list[PlanAlimentacionRead])
def listar_planes(
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PlanAlimentacion]:
    return (
        db.query(PlanAlimentacion)
        .options(_CARGA_DIAS)
        .filter(PlanAlimentacion.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{plan_id}", response_model=PlanAlimentacionRead)
def obtener_plan(
    plan_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanAlimentacion:
    return _get_plan_or_404(db, plan_id, usuario_actual.id)


@router.patch("/{plan_id}", response_model=PlanAlimentacionRead)
def actualizar_plan(
    plan_id: int,
    plan_in: PlanAlimentacionUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanAlimentacion:
    plan = _get_plan_or_404(db, plan_id, usuario_actual.id)

    datos = plan_in.model_dump(exclude_unset=True, exclude={"dias"})
    for campo, valor in datos.items():
        setattr(plan, campo, valor)

    if plan_in.dias is not None:
        _validar_comidas(db, plan_in.dias)

    try:
        # _reemplazar_dias hace un delete masivo que se ejecuta al momento (no se
        # difiere al commit), así que también tiene que ir dentro del try.
        if plan_in.dias is not None:
            _reemplazar_dias(db, plan.id, plan_in.dias)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar el plan de alimentación (datos duplicados o inválidos)",
        ) from exc

    return _get_plan_or_404(db, plan.id, usuario_actual.id)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(
    plan_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    plan = _get_plan_or_404(db, plan_id, usuario_actual.id)
    try:
        # El delete masivo de PlanDia se ejecuta al momento (no se difiere al commit),
        # así que si algún RegistroAlimentacion lo referencia, la violación de FK
        # salta aquí mismo — por eso también va dentro del try.
        db.query(PlanDia).filter(PlanDia.plan_id == plan.id).delete()
        db.delete(plan)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: el plan tiene registros de alimentación asociados",
        ) from exc
