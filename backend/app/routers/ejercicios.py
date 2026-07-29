from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Ejercicio, EjercicioGrupoMuscular, GrupoMuscular, Usuario
from app.schemas import EjercicioCreate, EjercicioGrupoMuscularInput, EjercicioRead, EjercicioUpdate
from app.security import get_current_user, require_admin

router = APIRouter(prefix="/ejercicios", tags=["ejercicios"])

_CARGA_GRUPOS_MUSCULARES = selectinload(Ejercicio.grupos_musculares).selectinload(
    EjercicioGrupoMuscular.grupo_muscular
)


def _get_ejercicio_or_404(db: Session, ejercicio_id: int) -> Ejercicio:
    ejercicio = (
        db.query(Ejercicio)
        .options(_CARGA_GRUPOS_MUSCULARES)
        .filter(Ejercicio.id == ejercicio_id)
        .first()
    )
    if ejercicio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado")
    return ejercicio


def _validar_grupos_musculares(db: Session, asociaciones: list[EjercicioGrupoMuscularInput]) -> None:
    ids = {asociacion.grupo_muscular_id for asociacion in asociaciones}
    if not ids:
        return
    encontrados = {id_ for (id_,) in db.query(GrupoMuscular.id).filter(GrupoMuscular.id.in_(ids)).all()}
    faltantes = ids - encontrados
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo(s) muscular(es) no encontrado(s): {sorted(faltantes)}",
        )


def _reemplazar_asociaciones(
    db: Session, ejercicio_id: int, asociaciones: list[EjercicioGrupoMuscularInput]
) -> None:
    db.query(EjercicioGrupoMuscular).filter(
        EjercicioGrupoMuscular.ejercicio_id == ejercicio_id
    ).delete()
    for asociacion in asociaciones:
        db.add(
            EjercicioGrupoMuscular(
                ejercicio_id=ejercicio_id,
                grupo_muscular_id=asociacion.grupo_muscular_id,
                es_principal=asociacion.es_principal,
            )
        )


@router.post("/", response_model=EjercicioRead, status_code=status.HTTP_201_CREATED)
def crear_ejercicio(
    ejercicio_in: EjercicioCreate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Ejercicio:
    _validar_grupos_musculares(db, ejercicio_in.grupos_musculares)

    ejercicio = Ejercicio(nombre=ejercicio_in.nombre, tipo=ejercicio_in.tipo)
    db.add(ejercicio)
    db.flush()
    _reemplazar_asociaciones(db, ejercicio.id, ejercicio_in.grupos_musculares)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear el ejercicio (datos duplicados o inválidos)",
        ) from exc

    return _get_ejercicio_or_404(db, ejercicio.id)


@router.get("/", response_model=list[EjercicioRead])
def listar_ejercicios(
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Ejercicio]:
    return (
        db.query(Ejercicio)
        .options(_CARGA_GRUPOS_MUSCULARES)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{ejercicio_id}", response_model=EjercicioRead)
def obtener_ejercicio(
    ejercicio_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Ejercicio:
    return _get_ejercicio_or_404(db, ejercicio_id)


@router.patch("/{ejercicio_id}", response_model=EjercicioRead)
def actualizar_ejercicio(
    ejercicio_id: int,
    ejercicio_in: EjercicioUpdate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Ejercicio:
    ejercicio = _get_ejercicio_or_404(db, ejercicio_id)

    datos = ejercicio_in.model_dump(exclude_unset=True, exclude={"grupos_musculares"})
    for campo, valor in datos.items():
        setattr(ejercicio, campo, valor)

    if ejercicio_in.grupos_musculares is not None:
        _validar_grupos_musculares(db, ejercicio_in.grupos_musculares)
        _reemplazar_asociaciones(db, ejercicio.id, ejercicio_in.grupos_musculares)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar el ejercicio (datos duplicados o inválidos)",
        ) from exc

    return _get_ejercicio_or_404(db, ejercicio.id)


@router.delete("/{ejercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ejercicio(
    ejercicio_id: int,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    ejercicio = _get_ejercicio_or_404(db, ejercicio_id)
    db.query(EjercicioGrupoMuscular).filter(
        EjercicioGrupoMuscular.ejercicio_id == ejercicio.id
    ).delete()
    db.delete(ejercicio)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: el ejercicio está en uso (ej. tiene series registradas)",
        ) from exc
