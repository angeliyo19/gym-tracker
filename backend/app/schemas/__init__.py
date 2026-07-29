from app.schemas.auth import Token, UsuarioRegistro
from app.schemas.comida import ComidaCreate, ComidaRead, ComidaUpdate
from app.schemas.ejercicio import (
    EjercicioCreate,
    EjercicioGrupoMuscularInput,
    EjercicioGrupoMuscularRead,
    EjercicioRead,
    EjercicioUpdate,
)
from app.schemas.grupo_muscular import GrupoMuscularCreate, GrupoMuscularRead, GrupoMuscularUpdate
from app.schemas.plan_alimentacion import (
    PlanAlimentacionCreate,
    PlanAlimentacionRead,
    PlanAlimentacionUpdate,
    PlanDiaInput,
    PlanDiaRead,
)
from app.schemas.registro_alimentacion import (
    RegistroAlimentacionCreate,
    RegistroAlimentacionRead,
    RegistroAlimentacionUpdate,
)
from app.schemas.registro_estado_animo import (
    RegistroEstadoAnimoCreate,
    RegistroEstadoAnimoRead,
    RegistroEstadoAnimoUpdate,
)
from app.schemas.registro_peso import RegistroPesoCreate, RegistroPesoRead, RegistroPesoUpdate
from app.schemas.rutina import (
    RutinaCreate,
    RutinaEjercicioInput,
    RutinaEjercicioRead,
    RutinaRead,
    RutinaUpdate,
)
from app.schemas.serie import SerieCreate, SerieRead, SerieUpdate
from app.schemas.sesion_entrenamiento import (
    IniciarRutinaRead,
    SeriesPorEjercicio,
    SesionDetalleRead,
    SesionEntrenamientoRead,
    UltimaSerieRef,
)
from app.schemas.usuario import UsuarioRead, UsuarioUpdate

__all__ = [
    "UsuarioUpdate",
    "UsuarioRead",
    "GrupoMuscularCreate",
    "GrupoMuscularUpdate",
    "GrupoMuscularRead",
    "EjercicioCreate",
    "EjercicioUpdate",
    "EjercicioRead",
    "EjercicioGrupoMuscularInput",
    "EjercicioGrupoMuscularRead",
    "RutinaCreate",
    "RutinaUpdate",
    "RutinaRead",
    "RutinaEjercicioInput",
    "RutinaEjercicioRead",
    "SesionEntrenamientoRead",
    "UltimaSerieRef",
    "IniciarRutinaRead",
    "SesionDetalleRead",
    "SeriesPorEjercicio",
    "SerieCreate",
    "SerieUpdate",
    "SerieRead",
    "ComidaCreate",
    "ComidaUpdate",
    "ComidaRead",
    "PlanAlimentacionCreate",
    "PlanAlimentacionUpdate",
    "PlanAlimentacionRead",
    "PlanDiaInput",
    "PlanDiaRead",
    "RegistroAlimentacionCreate",
    "RegistroAlimentacionUpdate",
    "RegistroAlimentacionRead",
    "RegistroPesoCreate",
    "RegistroPesoUpdate",
    "RegistroPesoRead",
    "RegistroEstadoAnimoCreate",
    "RegistroEstadoAnimoUpdate",
    "RegistroEstadoAnimoRead",
    "UsuarioRegistro",
    "Token",
]
