
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/esquema.py
#
# FUNCIÓN:
# Administrar las reglas del esquema de vacunación.
#
# ENDPOINTS:
# GET  /esquema/
# POST /esquema/
# PUT  /esquema/{regla_id}/estado
# POST /esquema/cargar-inicial
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from pydantic import (
    BaseModel,
    Field
)

from sqlalchemy.orm import Session

# Conexión con SQLite.

from backend.database import get_db

# Modelos de vacunas y reglas.

from backend.models.vacuna import Vacuna

from backend.models.esquema_dosis import EsquemaDosis

# Servicio que carga las reglas iniciales.

from backend.services.cargar_esquema_service import (
    cargar_calendario_2026
)


# ============================================================
# 2. CONFIGURAR ROUTER
# ============================================================

router = APIRouter(
    prefix="/esquema",
    tags=["Esquema de Vacunación"]
)


# ============================================================
# 3. MODELO PARA CREAR REGLAS
# ============================================================

# Pydantic valida los datos enviados a la API.

class EsquemaCrear(BaseModel):

    # Código de la vacuna.
    codigo_vacuna: str = Field(
        min_length=1,
        max_length=100
    )

    # Código específico de la dosis.
    codigo_dosis: str = Field(
        min_length=1,
        max_length=100
    )

    # Nombre de la dosis.
    nombre_dosis: str = Field(
        min_length=1,
        max_length=150
    )

    # Número de dosis.
    numero_dosis: Optional[int] = Field(
        default=None,
        ge=1
    )

    # Edad mínima en meses.
    edad_minima_meses: Optional[int] = Field(
        default=None,
        ge=0
    )

    # Edad recomendada en meses.
    edad_recomendada_meses: Optional[int] = Field(
        default=None,
        ge=0
    )

    # Edad máxima en meses.
    edad_maxima_meses: Optional[int] = Field(
        default=None,
        ge=0
    )

    # Tipo: primaria, refuerzo, unica, etc.
    tipo: Optional[str] = None

    # Campo de clasificación de la regla.
    obligatoria: bool = True

    # Observaciones.
    observaciones: Optional[str] = None


# ============================================================
# 4. CONVERTIR REGLA A DICCIONARIO
# ============================================================

def convertir_regla(regla):
    """
    Prepara la información de una regla
    para devolverla como JSON.

    Incluye el código de la vacuna asociada.
    """

    return {
        "id": regla.id,

        "codigo_vacuna": regla.vacuna.codigo,

        "codigo_dosis": regla.codigo_dosis,

        "nombre_dosis": regla.nombre_dosis,

        "numero_dosis": regla.numero_dosis,

        "edad_minima_meses": regla.edad_minima_meses,

        "edad_recomendada_meses": (
            regla.edad_recomendada_meses
        ),

        "edad_maxima_meses": regla.edad_maxima_meses,

        "tipo": regla.tipo,

        "obligatoria": regla.obligatoria,

        "activa": regla.activa,

        "observaciones": regla.observaciones
    }


# ============================================================
# 5. LISTAR REGLAS
# ============================================================

# ENDPOINT:
# GET /esquema/

@router.get("/")
def listar_esquema(
    db: Session = Depends(get_db)
):
    """
    Devuelve todas las reglas guardadas.

    Incluye tanto las reglas activas
    como las inactivas.
    """

    reglas = (
        db.query(EsquemaDosis)
        .order_by(
            EsquemaDosis.edad_recomendada_meses,
            EsquemaDosis.id
        )
        .all()
    )

    return [
        convertir_regla(regla)
        for regla in reglas
    ]


# ============================================================
# 6. CREAR REGLA MANUALMENTE
# ============================================================

# ENDPOINT:
# POST /esquema/

@router.post("/")
def crear_regla(
    datos: EsquemaCrear,
    db: Session = Depends(get_db)
):
    """
    Permite registrar una nueva regla.

    Por seguridad, queda inactiva hasta
    que sea validada.
    """

    # --------------------------------------------------------
    # VALIDAR RANGO DE EDADES
    # --------------------------------------------------------

    if (
        datos.edad_minima_meses is not None
        and datos.edad_maxima_meses is not None
        and datos.edad_minima_meses
        > datos.edad_maxima_meses
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "La edad mínima no puede superar "
                "la edad máxima."
            )
        )

    # --------------------------------------------------------
    # EVITAR CÓDIGOS DE DOSIS REPETIDOS
    # --------------------------------------------------------

    regla_existente = (
        db.query(EsquemaDosis)
        .filter(
            EsquemaDosis.codigo_dosis
            == datos.codigo_dosis
        )
        .first()
    )

    if regla_existente:

        raise HTTPException(
            status_code=409,
            detail="Ya existe una regla con ese código."
        )

    # --------------------------------------------------------
    # BUSCAR VACUNA
    # --------------------------------------------------------

    vacuna = (
        db.query(Vacuna)
        .filter(
            Vacuna.codigo == datos.codigo_vacuna
        )
        .first()
    )

    # --------------------------------------------------------
    # CREAR VACUNA SI NO EXISTE
    # --------------------------------------------------------

    if vacuna is None:

        vacuna = Vacuna(
            codigo=datos.codigo_vacuna,
            nombre=datos.nombre_dosis,
            activa=True
        )

        db.add(vacuna)

        db.flush()

    # --------------------------------------------------------
    # CREAR REGLA
    # --------------------------------------------------------

    regla = EsquemaDosis(
        vacuna_id=vacuna.id,

        codigo_dosis=datos.codigo_dosis,

        nombre_dosis=datos.nombre_dosis,

        numero_dosis=datos.numero_dosis,

        edad_minima_meses=datos.edad_minima_meses,

        edad_recomendada_meses=(
            datos.edad_recomendada_meses
        ),

        edad_maxima_meses=datos.edad_maxima_meses,

        tipo=datos.tipo,

        obligatoria=datos.obligatoria,

        # Todas las reglas nuevas comienzan inactivas.
        activa=False,

        observaciones=datos.observaciones
    )

    db.add(regla)

    db.commit()

    db.refresh(regla)

    return convertir_regla(regla)


# ============================================================
# 7. CAMBIAR ESTADO DE UNA REGLA
# ============================================================

# ENDPOINT:
# PUT /esquema/{regla_id}/estado?activa=false

@router.put("/{regla_id}/estado")
def cambiar_estado_regla(
    regla_id: int,
    activa: bool,
    db: Session = Depends(get_db)
):
    """
    Permite cambiar el estado de una regla.

    ADVERTENCIA:
    La activación debe reservarse para reglas
    verificadas por personal competente.
    """

    # --------------------------------------------------------
    # BUSCAR REGLA
    # --------------------------------------------------------

    regla = db.get(
        EsquemaDosis,
        regla_id
    )

    if regla is None:

        raise HTTPException(
            status_code=404,
            detail="Regla no encontrada."
        )

    # --------------------------------------------------------
    # CAMBIAR ESTADO
    # --------------------------------------------------------

    regla.activa = activa

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    db.commit()

    db.refresh(regla)

    return {
        "mensaje": (
            "Estado de la regla actualizado."
        ),
        "regla": convertir_regla(regla)
    }


# ============================================================
# 8. CARGAR CALENDARIO INICIAL
# ============================================================

# ENDPOINT:
# POST /esquema/cargar-inicial

@router.post("/cargar-inicial")
def cargar_esquema_inicial(
    db: Session = Depends(get_db)
):
    """
    Carga las reglas preliminares 2026.

    Si ya existen, no las duplica.

    Las nuevas reglas se crean inactivas.
    """

    return cargar_calendario_2026(
        db
    )
