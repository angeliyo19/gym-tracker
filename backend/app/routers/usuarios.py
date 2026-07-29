from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Usuario
from app.schemas import UsuarioRead, UsuarioUpdate
from app.security import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioRead)
def obtener_mi_perfil(usuario_actual: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario_actual


@router.patch("/me", response_model=UsuarioRead)
def actualizar_mi_perfil(
    usuario_in: UsuarioUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Usuario:
    for campo, valor in usuario_in.model_dump(exclude_unset=True).items():
        setattr(usuario_actual, campo, valor)
    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mi_perfil(
    usuario_actual: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    db.delete(usuario_actual)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: el usuario tiene rutinas o sesiones registradas",
        ) from exc
