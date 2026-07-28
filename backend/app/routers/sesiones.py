from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import SesionEntrenamiento, Usuario
from app.schemas import SesionEntrenamientoRead
from app.security import get_current_user

router = APIRouter(prefix="/sesiones", tags=["sesiones"])


def _get_sesion_or_404(db: Session, sesion_id: int, usuario_id: int) -> SesionEntrenamiento:
    sesion = (
        db.query(SesionEntrenamiento)
        .filter(SesionEntrenamiento.id == sesion_id, SesionEntrenamiento.usuario_id == usuario_id)
        .first()
    )
    if sesion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión de entrenamiento no encontrada"
        )
    return sesion


@router.post("/{sesion_id}/finalizar", response_model=SesionEntrenamientoRead)
def finalizar_sesion(
    sesion_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SesionEntrenamiento:
    """Marca la sesión como completada. Idempotente: si ya lo estaba, no es un error."""
    sesion = _get_sesion_or_404(db, sesion_id, usuario_actual.id)
    sesion.completada = True
    db.commit()
    db.refresh(sesion)
    return sesion
