
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
# BASE DE DATOS:
# SQL Server Express, mediante SQLAlchemy.
#
# IMPORTANTE:
# Este módulo solamente consulta información.
# No modifica pacientes ni registros de vacunación.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

# APIRouter permite agrupar los endpoints del Dashboard.
# Depends permite recibir la conexión a la base de datos.
from fastapi import APIRouter, Depends

# Session representa una sesión de SQLAlchemy.
from sqlalchemy.orm import Session

# func permite utilizar funciones SQL como UPPER y TRIM.
from sqlalchemy import func

# Importamos la función que proporciona la conexión
# a SQL Server desde la configuración del proyecto.
from backend.database import get_db

# Importamos los modelos de nuestras tablas.
from backend.models.paciente import Paciente
from backend.models.vacuna import Vacuna
from backend.models.aplicacion import Aplicacion
from backend.models.esquema_dosis import EsquemaDosis

from backend.models.equivalencia_vacuna import (
    EquivalenciaVacuna
)


# ============================================================
# 2. CONFIGURAR EL ROUTER
# ============================================================

# Todas las rutas de este archivo comienzan con /dashboard.
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
    Consulta y devuelve las estadísticas administrativas.

    Incluye:
    - Cantidad de pacientes.
    - Vacunas disponibles en el catálogo.
    - Aplicaciones registradas y anuladas.
    - Aplicaciones con fecha y sin fecha.
    - Registros provenientes de SISVACU.
    - Reglas del calendario.
    - Equivalencias de vacunas.

    NOTA:
    Los resultados no indican cobertura vacunal
    ni permiten determinar esquemas completos.
    """

    # ========================================================
    # 4. ESTADÍSTICAS DE PACIENTES
    # ========================================================

    # Contamos todos los pacientes registrados.
    total_pacientes = (
        db.query(Paciente)
        .count()
    )

    # Contamos pacientes que no tienen fecha de nacimiento.
    #
    # IS NULL es válido en SQL Server.
    # Por eso podemos utilizar .is_(None).
    pacientes_sin_fecha_nacimiento = (
        db.query(Paciente)
        .filter(
            Paciente.fecha_nacimiento.is_(None)
        )
        .count()
    )

    # ========================================================
    # 5. ESTADÍSTICAS DE VACUNAS
    # ========================================================

    # Contamos las vacunas del catálogo.
    total_vacunas = (
        db.query(Vacuna)
        .count()
    )

    # ========================================================
    # 6. ESTADÍSTICAS DE APLICACIONES
    # ========================================================

    # Contamos todas las aplicaciones registradas,
    # incluyendo las que fueron anuladas.
    total_aplicaciones = (
        db.query(Aplicacion)
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES NO ANULADAS
    # --------------------------------------------------------

    # CORRECCIÓN PARA SQL SERVER:
    #
    # Antes:
    # Aplicacion.anulada.is_(False)
    #
    # Eso generaba:
    # WHERE aplicaciones.anulada IS 0
    #
    # SQL Server no admite IS 0.
    #
    # Ahora utilizamos == 0, que genera una
    # comparación de igualdad compatible.
    aplicaciones_no_anuladas = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada == 0
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES ANULADAS
    # --------------------------------------------------------

    # El valor 1 indica que la aplicación está anulada.
    aplicaciones_anuladas = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada == 1
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES SIN FECHA
    # --------------------------------------------------------

    # Contamos aplicaciones que:
    # 1. No están anuladas.
    # 2. No tienen fecha de aplicación.
    aplicaciones_sin_fecha = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada == 0,
            Aplicacion.fecha_aplicacion.is_(None)
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES CON FECHA
    # --------------------------------------------------------

    # Contamos aplicaciones que:
    # 1. No están anuladas.
    # 2. Tienen una fecha registrada.
    aplicaciones_con_fecha = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada == 0,
            Aplicacion.fecha_aplicacion.isnot(None)
        )
        .count()
    )

    # ========================================================
    # 7. ESTADÍSTICAS DE ORIGEN SISVACU
    # ========================================================

    # Contamos aplicaciones no anuladas cuyo origen
    # sea SISVACU.
    #
    # TRIM elimina espacios al inicio y al final.
    # UPPER convierte el texto a mayúsculas.
    #
    # Esto permite reconocer, por ejemplo:
    # "sisvacu", "SISVACU" y " SISVACU ".
    aplicaciones_sisvacu = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.anulada == 0,
            func.upper(
                func.trim(Aplicacion.origen)
            ) == "SISVACU"
        )
        .count()
    )

    # --------------------------------------------------------
    # APLICACIONES DE OTROS ORÍGENES
    # --------------------------------------------------------

    # Calculamos cuántas aplicaciones no anuladas
    # no están identificadas como SISVACU.
    #
    # También incluye registros cuyo origen es NULL
    # o no está especificado.
    aplicaciones_otros_origenes = (
        aplicaciones_no_anuladas
        - aplicaciones_sisvacu
    )

    # ========================================================
    # 8. ESTADÍSTICAS DEL CALENDARIO
    # ========================================================

    # Contamos todas las reglas del esquema.
    total_reglas = (
        db.query(EsquemaDosis)
        .count()
    )

    # CORRECCIÓN PARA SQL SERVER:
    #
    # Antes:
    # EsquemaDosis.activa.is_(True)
    #
    # Si el campo almacena 0 y 1, la comparación
    # correcta es == 1.
    reglas_activas = (
        db.query(EsquemaDosis)
        .filter(
            EsquemaDosis.activa == 1
        )
        .count()
    )

    # Las reglas inactivas se obtienen restando
    # las activas del total de reglas.
    reglas_inactivas = (
        total_reglas
        - reglas_activas
    )

    # ========================================================
    # 9. ESTADÍSTICAS DE EQUIVALENCIAS
    # ========================================================

    # Cantidad total de equivalencias registradas.
    total_equivalencias = (
        db.query(EquivalenciaVacuna)
        .count()
    )

    # Equivalencias cuyo estado es "verificada".
    equivalencias_verificadas = (
        db.query(EquivalenciaVacuna)
        .filter(
            EquivalenciaVacuna.estado == "verificada"
        )
        .count()
    )

    # Equivalencias pendientes de verificación.
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

    # Solamente calculamos porcentajes si existen
    # aplicaciones no anuladas.
    #
    # Así evitamos una división entre cero.
    if aplicaciones_no_anuladas > 0:

        # Porcentaje de aplicaciones provenientes
        # de SISVACU.
        porcentaje_sisvacu = round(
            (
                aplicaciones_sisvacu
                / aplicaciones_no_anuladas
            ) * 100,
            2
        )

        # Porcentaje de aplicaciones sin fecha.
        porcentaje_sin_fecha = round(
            (
                aplicaciones_sin_fecha
                / aplicaciones_no_anuladas
            ) * 100,
            2
        )

    else:

        # Si no existen aplicaciones, ambos
        # porcentajes se establecen en cero.
        porcentaje_sisvacu = 0
        porcentaje_sin_fecha = 0

    # ========================================================
    # 11. DEVOLVER LAS ESTADÍSTICAS A REACT
    # ========================================================

    # FastAPI convierte automáticamente este
    # diccionario de Python en una respuesta JSON.
    #
    # Conservamos las mismas claves para que el
    # frontend pueda mostrar los datos correctamente.
    return {

        # -----------------------------------------------
        # PACIENTES
        # -----------------------------------------------
        "pacientes": {
            "total": total_pacientes,

            "sin_fecha_nacimiento": (
                pacientes_sin_fecha_nacimiento
            )
        },

        # -----------------------------------------------
        # VACUNAS
        # -----------------------------------------------
        "vacunas": {
            "total_catalogo": total_vacunas
        },

        # -----------------------------------------------
        # APLICACIONES
        # -----------------------------------------------
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

        # -----------------------------------------------
        # ORIGEN DE LOS REGISTROS
        # -----------------------------------------------
        "origen_registros": {
            "sisvacu": aplicaciones_sisvacu,

            "otros": aplicaciones_otros_origenes,

            "porcentaje_sisvacu": (
                porcentaje_sisvacu
            )
        },

        # -----------------------------------------------
        # CALENDARIO
        # -----------------------------------------------
        "calendario": {
            "total_reglas": total_reglas,

            "reglas_activas": reglas_activas,

            "reglas_inactivas": reglas_inactivas
        },

        # -----------------------------------------------
        # EQUIVALENCIAS
        # -----------------------------------------------
        "equivalencias": {
            "total": total_equivalencias,

            "verificadas": equivalencias_verificadas,

            "pendientes": equivalencias_pendientes
        },

        # -----------------------------------------------
        # ADVERTENCIA ADMINISTRATIVA
        # -----------------------------------------------
        "advertencia": (
            "Estas estadísticas describen registros "
            "administrativos. No representan cobertura "
            "vacunal ni determinan esquemas completos."
        )
    }
