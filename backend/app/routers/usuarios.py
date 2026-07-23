from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _get_usuario_or_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)) -> Usuario:
    usuario = Usuario(**usuario_in.model_dump())
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from exc
    db.refresh(usuario)
    return usuario


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)) -> Usuario:
    return _get_usuario_or_404(db, usuario_id)


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int, usuario_in: UsuarioUpdate, db: Session = Depends(get_db)
) -> Usuario:
    usuario = _get_usuario_or_404(db, usuario_id)
    for campo, valor in usuario_in.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from exc
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)) -> None:
    usuario = _get_usuario_or_404(db, usuario_id)
    db.delete(usuario)
    db.commit()
