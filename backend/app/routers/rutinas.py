from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import (
    Ejercicio,
    EjercicioGrupoMuscular,
    Rutina,
    RutinaEjercicio,
    SesionEntrenamiento,
    Usuario,
)
from app.schemas import (
    RutinaCreate,
    RutinaEjercicioInput,
    RutinaRead,
    RutinaUpdate,
    SesionEntrenamientoRead,
)

router = APIRouter(prefix="/rutinas", tags=["rutinas"])

_CARGA_EJERCICIOS = selectinload(Rutina.ejercicios).options(
    selectinload(RutinaEjercicio.ejercicio)
    .selectinload(Ejercicio.grupos_musculares)
    .selectinload(EjercicioGrupoMuscular.grupo_muscular)
)


def _get_rutina_or_404(db: Session, rutina_id: int) -> Rutina:
    rutina = (
        db.query(Rutina).options(_CARGA_EJERCICIOS).filter(Rutina.id == rutina_id).first()
    )
    if rutina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    return rutina


def _validar_usuario(db: Session, usuario_id: int) -> None:
    if db.get(Usuario, usuario_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


def _validar_ejercicios(db: Session, asociaciones: list[RutinaEjercicioInput]) -> None:
    ids = {asociacion.ejercicio_id for asociacion in asociaciones}
    if not ids:
        return
    encontrados = {id_ for (id_,) in db.query(Ejercicio.id).filter(Ejercicio.id.in_(ids)).all()}
    faltantes = ids - encontrados
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejercicio(s) no encontrado(s): {sorted(faltantes)}",
        )


def _reemplazar_ejercicios(
    db: Session, rutina_id: int, asociaciones: list[RutinaEjercicioInput]
) -> None:
    db.query(RutinaEjercicio).filter(RutinaEjercicio.rutina_id == rutina_id).delete()
    for asociacion in asociaciones:
        db.add(
            RutinaEjercicio(
                rutina_id=rutina_id,
                ejercicio_id=asociacion.ejercicio_id,
                orden=asociacion.orden,
                series_objetivo=asociacion.series_objetivo,
                repeticiones_objetivo=asociacion.repeticiones_objetivo,
            )
        )


@router.post("/", response_model=RutinaRead, status_code=status.HTTP_201_CREATED)
def crear_rutina(rutina_in: RutinaCreate, db: Session = Depends(get_db)) -> Rutina:
    _validar_usuario(db, rutina_in.usuario_id)
    _validar_ejercicios(db, rutina_in.ejercicios)

    rutina = Rutina(usuario_id=rutina_in.usuario_id, nombre=rutina_in.nombre)
    db.add(rutina)
    db.flush()
    _reemplazar_ejercicios(db, rutina.id, rutina_in.ejercicios)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear la rutina (datos duplicados o inválidos)",
        ) from exc

    return _get_rutina_or_404(db, rutina.id)


@router.get("/", response_model=list[RutinaRead])
def listar_rutinas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[Rutina]:
    return db.query(Rutina).options(_CARGA_EJERCICIOS).offset(skip).limit(limit).all()


@router.get("/{rutina_id}", response_model=RutinaRead)
def obtener_rutina(rutina_id: int, db: Session = Depends(get_db)) -> Rutina:
    return _get_rutina_or_404(db, rutina_id)


@router.patch("/{rutina_id}", response_model=RutinaRead)
def actualizar_rutina(
    rutina_id: int, rutina_in: RutinaUpdate, db: Session = Depends(get_db)
) -> Rutina:
    rutina = _get_rutina_or_404(db, rutina_id)

    datos = rutina_in.model_dump(exclude_unset=True, exclude={"ejercicios"})
    for campo, valor in datos.items():
        setattr(rutina, campo, valor)

    if rutina_in.ejercicios is not None:
        _validar_ejercicios(db, rutina_in.ejercicios)
        _reemplazar_ejercicios(db, rutina.id, rutina_in.ejercicios)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar la rutina (datos duplicados o inválidos)",
        ) from exc

    return _get_rutina_or_404(db, rutina.id)


@router.delete("/{rutina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rutina(rutina_id: int, db: Session = Depends(get_db)) -> None:
    rutina = _get_rutina_or_404(db, rutina_id)
    db.query(RutinaEjercicio).filter(RutinaEjercicio.rutina_id == rutina.id).delete()
    db.delete(rutina)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la rutina tiene sesiones de entrenamiento registradas",
        ) from exc


@router.post(
    "/{rutina_id}/iniciar", response_model=SesionEntrenamientoRead, status_code=status.HTTP_201_CREATED
)
def iniciar_rutina(rutina_id: int, db: Session = Depends(get_db)) -> SesionEntrenamiento:
    rutina = _get_rutina_or_404(db, rutina_id)

    sesion = SesionEntrenamiento(
        usuario_id=rutina.usuario_id, rutina_id=rutina.id, fecha=date.today()
    )
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return sesion
