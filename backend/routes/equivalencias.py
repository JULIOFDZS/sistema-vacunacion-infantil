
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/equivalencias.py
#
# FUNCIÓN:
# Administrar las equivalencias entre códigos SISVACU
# y códigos del calendario.
#
# ENDPOINTS:
# GET  /equivalencias/
# POST /equivalencias/
# PUT  /equivalencias/{equivalencia_id}/verificar
#
# IMPORTANTE:
# Registrar una equivalencia no la verifica.
# ============================================================

from datetime import datetime
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

from backend.database import get_db

from backend.models.vacuna import Vacuna

from backend.models.esquema_dosis import EsquemaDosis

from backend.models.equivalencia_vacuna import (
    EquivalenciaVacuna
)


# ============================================================
# 1. CONFIGURAR ROUTER
# ============================================================

router = APIRouter(
    prefix="/equivalencias",
    tags=["Equivalencias SISVACU"]
)


# ============================================================
# 2. MODELO PARA REGISTRAR EQUIVALENCIAS
# ============================================================

class EquivalenciaCrear(BaseModel):

    codigo_sisvacu: str = Field(
        min_length=1,
        max_length=100
    )

    codigo_calendario: str = Field(
        min_length=1,
        max_length=100
    )

    observaciones: Optional[str] = None


# ============================================================
# 3. MODELO PARA VERIFICAR EQUIVALENCIAS
# ============================================================

class EquivalenciaVerificar(BaseModel):

    # Documento o referencia utilizada para verificar.
    fuente_verificacion: str = Field(
        min_length=5
    )

    # Nombre de la persona que realizó la revisión.
    verificado_por: str = Field(
        min_length=3,
        max_length=150
    )

    observaciones: Optional[str] = None


# ============================================================
# 4. CONVERTIR RESULTADO A JSON
# ============================================================

def convertir_equivalencia(equivalencia):

    return {
        "id": equivalencia.id,

        "codigo_sisvacu": (
            equivalencia.codigo_sisvacu
        ),

        "codigo_calendario": (
            equivalencia.codigo_calendario
        ),

        "estado": equivalencia.estado,

        "fuente_verificacion": (
            equivalencia.fuente_verificacion
        ),

        "verificado_por": (
            equivalencia.verificado_por
        ),

        "observaciones": (
            equivalencia.observaciones
        ),

        "creado_en": (
            equivalencia.creado_en
        ),

        "verificado_en": (
            equivalencia.verificado_en
        )
    }


# ============================================================
# 5. LISTAR EQUIVALENCIAS
# ============================================================

@router.get("/")
def listar_equivalencias(
    db: Session = Depends(get_db)
):
    """
    Devuelve todas las equivalencias registradas,
    tanto pendientes como verificadas.
    """

    equivalencias = (
        db.query(EquivalenciaVacuna)
        .order_by(EquivalenciaVacuna.id)
        .all()
    )

    return [
        convertir_equivalencia(equivalencia)
        for equivalencia in equivalencias
    ]


# ============================================================
# 6. REGISTRAR EQUIVALENCIA
# ============================================================

@router.post("/")
def crear_equivalencia(
    datos: EquivalenciaCrear,
    db: Session = Depends(get_db)
):
    """
    Registra una posible correspondencia entre
    un código SISVACU y una dosis del calendario.

    Toda equivalencia nueva queda pendiente.
    """

    # --------------------------------------------------------
    # NORMALIZAR CÓDIGOS
    # --------------------------------------------------------

    codigo_sisvacu = (
        datos.codigo_sisvacu.strip().upper()
    )

    codigo_calendario = (
        datos.codigo_calendario.strip().upper()
    )

    # --------------------------------------------------------
    # VERIFICAR QUE EXISTE EL CÓDIGO SISVACU
    # --------------------------------------------------------

    vacuna = (
        db.query(Vacuna)
        .filter(
            Vacuna.codigo == codigo_sisvacu
        )
        .first()
    )

    if vacuna is None:

        raise HTTPException(
            status_code=404,
            detail="El código SISVACU no existe."
        )

    # --------------------------------------------------------
    # VERIFICAR QUE EXISTE LA REGLA DEL CALENDARIO
    # --------------------------------------------------------

    regla = (
        db.query(EsquemaDosis)
        .filter(
            EsquemaDosis.codigo_dosis
            == codigo_calendario
        )
        .first()
    )

    if regla is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "El código del calendario no existe."
            )
        )

    # --------------------------------------------------------
    # EVITAR DUPLICADOS
    # --------------------------------------------------------

    existente = (
        db.query(EquivalenciaVacuna)
        .filter(
            EquivalenciaVacuna.codigo_sisvacu
            == codigo_sisvacu,

            EquivalenciaVacuna.codigo_calendario
            == codigo_calendario
        )
        .first()
    )

    if existente:

        raise HTTPException(
            status_code=409,
            detail="Esta equivalencia ya existe."
        )

    # --------------------------------------------------------
    # CREAR EQUIVALENCIA PENDIENTE
    # --------------------------------------------------------

    equivalencia = EquivalenciaVacuna(
        codigo_sisvacu=codigo_sisvacu,
        codigo_calendario=codigo_calendario,

        estado="pendiente",

        observaciones=datos.observaciones
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    db.add(equivalencia)

    db.commit()

    db.refresh(equivalencia)

    return convertir_equivalencia(
        equivalencia
    )


# ============================================================
# 7. VERIFICAR EQUIVALENCIA
# ============================================================

@router.put("/{equivalencia_id}/verificar")
def verificar_equivalencia(
    equivalencia_id: int,
    datos: EquivalenciaVerificar,
    db: Session = Depends(get_db)
):
    """
    Marca una equivalencia como verificada.

    Debe utilizarse únicamente después de revisar
    la documentación correspondiente.
    """

    # --------------------------------------------------------
    # BUSCAR EQUIVALENCIA
    # --------------------------------------------------------

    equivalencia = db.get(
        EquivalenciaVacuna,
        equivalencia_id
    )

    if equivalencia is None:

        raise HTTPException(
            status_code=404,
            detail="Equivalencia no encontrada."
        )

    # --------------------------------------------------------
    # COMPROBAR QUE NO ESTÁ VERIFICADA
    # --------------------------------------------------------

    if equivalencia.estado == "verificada":

        raise HTTPException(
            status_code=409,
            detail=(
                "Esta equivalencia ya está verificada."
            )
        )

    # --------------------------------------------------------
    # GUARDAR INFORMACIÓN DE VERIFICACIÓN
    # --------------------------------------------------------

    equivalencia.estado = "verificada"

    equivalencia.fuente_verificacion = (
        datos.fuente_verificacion.strip()
    )

    equivalencia.verificado_por = (
        datos.verificado_por.strip()
    )

    equivalencia.observaciones = (
        datos.observaciones
    )

    equivalencia.verificado_en = (
        datetime.now()
    )

    # --------------------------------------------------------
    # CONFIRMAR CAMBIOS
    # --------------------------------------------------------

    db.commit()

    db.refresh(equivalencia)

    return convertir_equivalencia(
        equivalencia
    )
