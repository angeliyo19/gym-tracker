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
    Serie,
    SesionEntrenamiento,
    Usuario,
)
from app.schemas import (
    IniciarRutinaRead,
    RutinaCreate,
    RutinaEjercicioInput,
    RutinaRead,
    RutinaUpdate,
    UltimaSerieRef,
)
from app.security import get_current_user

router = APIRouter(prefix="/rutinas", tags=["rutinas"])

_CARGA_EJERCICIOS = selectinload(Rutina.ejercicios).options(
    selectinload(RutinaEjercicio.ejercicio)
    .selectinload(Ejercicio.grupos_musculares)
    .selectinload(EjercicioGrupoMuscular.grupo_muscular)
)


def _get_rutina_or_404(db: Session, rutina_id: int, usuario_id: int) -> Rutina:
    rutina = (
        db.query(Rutina)
        .options(_CARGA_EJERCICIOS)
        .filter(Rutina.id == rutina_id, Rutina.usuario_id == usuario_id)
        .first()
    )
    if rutina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    return rutina


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
def crear_rutina(
    rutina_in: RutinaCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Rutina:
    if not rutina_in.ejercicios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La rutina debe tener al menos un ejercicio",
        )
    _validar_ejercicios(db, rutina_in.ejercicios)

    rutina = Rutina(usuario_id=usuario_actual.id, nombre=rutina_in.nombre)
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

    return _get_rutina_or_404(db, rutina.id, usuario_actual.id)


@router.get("/", response_model=list[RutinaRead])
def listar_rutinas(
    skip: int = 0,
    limit: int = 100,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Rutina]:
    return (
        db.query(Rutina)
        .options(_CARGA_EJERCICIOS)
        .filter(Rutina.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{rutina_id}", response_model=RutinaRead)
def obtener_rutina(
    rutina_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Rutina:
    return _get_rutina_or_404(db, rutina_id, usuario_actual.id)


@router.patch("/{rutina_id}", response_model=RutinaRead)
def actualizar_rutina(
    rutina_id: int,
    rutina_in: RutinaUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Rutina:
    rutina = _get_rutina_or_404(db, rutina_id, usuario_actual.id)

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

    return _get_rutina_or_404(db, rutina.id, usuario_actual.id)


@router.delete("/{rutina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rutina(
    rutina_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    rutina = _get_rutina_or_404(db, rutina_id, usuario_actual.id)
    try:
        db.query(RutinaEjercicio).filter(RutinaEjercicio.rutina_id == rutina.id).delete()
        db.delete(rutina)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la rutina tiene sesiones de entrenamiento registradas",
        ) from exc


def _ultima_serie_de_ejercicio(
    db: Session, usuario_id: int, ejercicio_id: int
) -> tuple[Serie, date] | None:
    return (
        db.query(Serie, SesionEntrenamiento.fecha)
        .join(SesionEntrenamiento, Serie.sesion_id == SesionEntrenamiento.id)
        .filter(
            SesionEntrenamiento.usuario_id == usuario_id,
            Serie.ejercicio_id == ejercicio_id,
        )
        .order_by(SesionEntrenamiento.fecha.desc(), Serie.id.desc())
        .first()
    )


def construir_ultimas_series(
    db: Session, usuario_id: int, ejercicio_ids: set[int]
) -> list[UltimaSerieRef]:
    ultimas_series = []
    for ejercicio_id in ejercicio_ids:
        resultado = _ultima_serie_de_ejercicio(db, usuario_id, ejercicio_id)
        if resultado is not None:
            serie, fecha = resultado
            ultimas_series.append(
                UltimaSerieRef(
                    ejercicio_id=ejercicio_id,
                    peso=serie.peso,
                    repeticiones=serie.repeticiones,
                    fecha=fecha,
                )
            )
    return ultimas_series


@router.post(
    "/{rutina_id}/iniciar", response_model=IniciarRutinaRead, status_code=status.HTTP_201_CREATED
)
def iniciar_rutina(
    rutina_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IniciarRutinaRead:
    rutina = _get_rutina_or_404(db, rutina_id, usuario_actual.id)

    sesion = SesionEntrenamiento(
        usuario_id=usuario_actual.id, rutina_id=rutina.id, fecha=date.today()
    )
    db.add(sesion)
    db.commit()
    db.refresh(sesion)

    ejercicio_ids = {asociacion.ejercicio_id for asociacion in rutina.ejercicios}
    ultimas_series = construir_ultimas_series(db, usuario_actual.id, ejercicio_ids)

    return IniciarRutinaRead(
        id=sesion.id,
        usuario_id=sesion.usuario_id,
        rutina_id=sesion.rutina_id,
        fecha=sesion.fecha,
        notas=sesion.notas,
        completada=sesion.completada,
        hora_inicio=sesion.hora_inicio,
        hora_fin=sesion.hora_fin,
        ultimas_series=ultimas_series,
    )
