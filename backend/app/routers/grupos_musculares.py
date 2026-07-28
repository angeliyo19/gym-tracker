from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import GrupoMuscular
from app.schemas import GrupoMuscularCreate, GrupoMuscularRead, GrupoMuscularUpdate

router = APIRouter(prefix="/grupos-musculares", tags=["grupos-musculares"])


def _get_grupo_muscular_or_404(db: Session, grupo_muscular_id: int) -> GrupoMuscular:
    grupo = db.get(GrupoMuscular, grupo_muscular_id)
    if grupo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo muscular no encontrado")
    return grupo


@router.post("/", response_model=GrupoMuscularRead, status_code=status.HTTP_201_CREATED)
def crear_grupo_muscular(grupo_in: GrupoMuscularCreate, db: Session = Depends(get_db)) -> GrupoMuscular:
    grupo = GrupoMuscular(**grupo_in.model_dump())
    db.add(grupo)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un grupo muscular con ese nombre",
        ) from exc
    db.refresh(grupo)
    return grupo


@router.get("/", response_model=list[GrupoMuscularRead])
def listar_grupos_musculares(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[GrupoMuscular]:
    return db.query(GrupoMuscular).offset(skip).limit(limit).all()


@router.get("/{grupo_muscular_id}", response_model=GrupoMuscularRead)
def obtener_grupo_muscular(grupo_muscular_id: int, db: Session = Depends(get_db)) -> GrupoMuscular:
    return _get_grupo_muscular_or_404(db, grupo_muscular_id)


@router.patch("/{grupo_muscular_id}", response_model=GrupoMuscularRead)
def actualizar_grupo_muscular(
    grupo_muscular_id: int, grupo_in: GrupoMuscularUpdate, db: Session = Depends(get_db)
) -> GrupoMuscular:
    grupo = _get_grupo_muscular_or_404(db, grupo_muscular_id)
    for campo, valor in grupo_in.model_dump(exclude_unset=True).items():
        setattr(grupo, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un grupo muscular con ese nombre",
        ) from exc
    db.refresh(grupo)
    return grupo


@router.delete("/{grupo_muscular_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_grupo_muscular(grupo_muscular_id: int, db: Session = Depends(get_db)) -> None:
    grupo = _get_grupo_muscular_or_404(db, grupo_muscular_id)
    db.delete(grupo)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: el grupo muscular está en uso por algún ejercicio",
        ) from exc
