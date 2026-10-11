
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/dashboard.py
#
# FUNCIÓN:
# Consultar estadísticas generales del sistema.
#
# ENDPOINT:
# GET /dashboard/resumen
#
# IMPORTANTE:
# Este módulo solo consulta datos.
# No modifica registros de vacunación.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from sqlalchemy import func

# Conexión a SQLite.

from backend.database import get_db

# Modelos de la base de datos.

from backend.models.paciente import Paciente

from backend.models.vacuna import Vacuna

from backend.models.aplicacion import Aplicacion

from backend.models.esquema_dosis import EsquemaDosis

from backend.models.equivalencia_vacuna import (
    EquivalenciaVacuna
)


# ============================================================
# 2. CONFIGURAR ROUTER
# ============================================================

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Administrativo"]
)


# ============================================================
# 3. ENDPOINT DEL RESUMEN GENERAL
# ============================================================

@router.get("/resumen")
def obtener_resumen_dashboard(
    db: Session = Depends(get_db)
):
    """
    Consulta los datos generales del sistema.

    Devuelve:
    - Total de pacientes.
    - Total de vacunas del catálogo.
    - Aplicaciones registradas.
    - Aplicaciones anuladas.
    - Aplicaciones sin fecha.
    - Registros SISVACU.
    - Reglas del calendario.
    - Equivalencias registradas.
    """

    # ========================================================
    # 4. CONTAR PACIENTES
    # ========================================================

    total_pacientes = (
        db.query(Paciente)
        .count()
    )

    # --------------------------------------------------------
    # PACIENTES SIN FECHA DE NACIMIENTO
    # --------------------------------------------------------

    pacientes_sin_fecha_nacimiento = (
        db.query(Paciente)
        .filter(
            Paciente.fecha_nacimiento.is_(None)
        )
        .count()
    )

    # ========================================================
    # 5. CONTAR VACUNAS
    # ========================================================

    total_vacunas = (
        db.query(Vacuna)
        .count()
    )

    # ========================================================
    # 6. CONTAR APLICACIONES
    # ========================================================

    total_aplicaciones = (
        db.query(Aplicacion)
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES NO ANULADAS
    # --------------------------------------------------------

    aplicaciones_no_anuladas = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada.is_(False)
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES ANULADAS
    # --------------------------------------------------------

    aplicaciones_anuladas = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada.is_(True)
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES SIN FECHA
    # --------------------------------------------------------

    aplicaciones_sin_fecha = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada.is_(False),
            Aplicacion.fecha_aplicacion.is_(None)
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES CON FECHA
    # --------------------------------------------------------

    aplicaciones_con_fecha = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada.is_(False),
            Aplicacion.fecha_aplicacion.isnot(None)
        )
        .count()
    )

    # ========================================================
    # 7. CONTAR REGISTROS SISVACU
    # ========================================================

    # Utilizamos trim y upper para reconocer
    # variaciones del texto SISVACU.

    aplicaciones_sisvacu = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada.is_(False),
            func.upper(
                func.trim(Aplicacion.origen)
            ) == "SISVACU"
        )
        .count()
    )

    # --------------------------------------------------------
    # OTROS ORÍGENES
    # --------------------------------------------------------

    aplicaciones_otros_origenes = (
        aplicaciones_no_anuladas
        - aplicaciones_sisvacu
    )

    # ========================================================
    # 8. CONTAR REGLAS DEL CALENDARIO
    # ========================================================

    total_reglas = (
        db.query(EsquemaDosis)
        .count()
    )

    reglas_activas = (
        db.query(EsquemaDosis)
        .filter(
            EsquemaDosis.activa.is_(True)
        )
        .count()
    )

    reglas_inactivas = (
        total_reglas
        - reglas_activas
    )

    # ========================================================
    # 9. CONTAR EQUIVALENCIAS
    # ========================================================

    total_equivalencias = (
        db.query(EquivalenciaVacuna)
        .count()
    )

    equivalencias_verificadas = (
        db.query(EquivalenciaVacuna)
        .filter(
            EquivalenciaVacuna.estado == "verificada"
        )
        .count()
    )

    equivalencias_pendientes = (
        db.query(EquivalenciaVacuna)
        .filter(
            EquivalenciaVacuna.estado == "pendiente"
        )
        .count()
    )

    # ========================================================
    # 10. CALCULAR PORCENTAJES
    # ========================================================

    # Evitamos dividir entre cero.

    if aplicaciones_no_anuladas > 0:

        porcentaje_sisvacu = round(
            (
                aplicaciones_sisvacu
                / aplicaciones_no_anuladas
            ) * 100,
            2
        )

        porcentaje_sin_fecha = round(
            (
                aplicaciones_sin_fecha
                / aplicaciones_no_anuladas
            ) * 100,
            2
        )

    else:

        porcentaje_sisvacu = 0

        porcentaje_sin_fecha = 0

    # ========================================================
    # 11. DEVOLVER RESULTADO
    # ========================================================

    return {

        "pacientes": {

            "total": total_pacientes,

            "sin_fecha_nacimiento": (
                pacientes_sin_fecha_nacimiento
            )
        },

        "vacunas": {

            "total_catalogo": total_vacunas
        },

        "aplicaciones": {

            "total_registros": total_aplicaciones,

            "no_anuladas": aplicaciones_no_anuladas,

            "anuladas": aplicaciones_anuladas,

            "con_fecha": aplicaciones_con_fecha,

            "sin_fecha": aplicaciones_sin_fecha,

            "porcentaje_sin_fecha": (
                porcentaje_sin_fecha
            )
        },

        "origen_registros": {

            "sisvacu": aplicaciones_sisvacu,

            "otros": aplicaciones_otros_origenes,

            "porcentaje_sisvacu": (
                porcentaje_sisvacu
            )
        },

        "calendario": {

            "total_reglas": total_reglas,

            "reglas_activas": reglas_activas,

            "reglas_inactivas": reglas_inactivas
        },

        "equivalencias": {

            "total": total_equivalencias,

            "verificadas": equivalencias_verificadas,

            "pendientes": equivalencias_pendientes
        },

        "advertencia": (
            "Estas estadísticas describen registros "
            "administrativos. No representan cobertura "
            "vacunal ni determinan esquemas completos."
        )
    }
