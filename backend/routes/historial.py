
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/historial.py
#
# FUNCIÓN:
# Consultar el historial individual de vacunación
# de un paciente registrado en nuestro sistema.
#
# ENDPOINTS:
# GET /historial/paciente/{paciente_id}
# GET /historial/paciente/{paciente_id}/resumen
#
# IMPORTANTE:
# Este módulo es de solo lectura.
# No modifica registros ni determina dosis pendientes.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

# FastAPI:
# APIRouter: organiza las rutas.
# Depends: permite obtener la sesión de SQLite.
# HTTPException: devuelve errores HTTP.

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

# Session:
# Permite consultar la base de datos.

from sqlalchemy.orm import Session

# Conexión a SQLite.

from backend.database import get_db

# Modelos de nuestra base de datos.

from backend.models.paciente import Paciente

from backend.models.identificador import (
    IdentificadorPaciente
)

from backend.models.aplicacion import Aplicacion


# ============================================================
# 2. CONFIGURAR ROUTER
# ============================================================

# Todas las rutas comenzarán con:
#
# /historial

router = APIRouter(
    prefix="/historial",
    tags=["Historial de Vacunación"]
)


# ============================================================
# 3. CONVERTIR FECHA A TEXTO
# ============================================================

def convertir_fecha(fecha):
    """
    Convierte una fecha a formato ISO.

    Ejemplo:
        2026-05-10

    Si la fecha no está registrada,
    devuelve None, que FastAPI representa
    como null en JSON.
    """

    if fecha is None:
        return None

    return fecha.isoformat()


# ============================================================
# 4. OBTENER DATOS DEL PACIENTE
# ============================================================

def obtener_datos_paciente(paciente):
    """
    Prepara los datos generales del paciente
    para mostrarlos en el historial.
    """

    return {
        "id": paciente.id,

        "nombres": paciente.nombres,

        "apellidos": paciente.apellidos,

        "nombre_completo": (
            f"{paciente.nombres} {paciente.apellidos}"
        ),

        "fecha_nacimiento": convertir_fecha(
            paciente.fecha_nacimiento
        ),

        "edad_reportada_anios": (
            paciente.edad_reportada_anios
        ),

        "sexo": paciente.sexo,

        "estado": paciente.estado,

        "completitud": paciente.completitud
    }


# ============================================================
# 5. CONSULTAR IDENTIFICADORES
# ============================================================

def obtener_identificadores(paciente_id, db: Session):
    """
    Obtiene los identificadores registrados
    para un paciente.

    Ejemplos:
    - Cédula.
    - Identificador temporal SISVACU.

    No supone que un código temporal
    pertenece a un padre o tutor.
    """

    identificadores = (
        db.query(IdentificadorPaciente)
        .filter(
            IdentificadorPaciente.paciente_id
            == paciente_id
        )
        .order_by(
            IdentificadorPaciente.id
        )
        .all()
    )

    resultado = []

    for identificador in identificadores:

        resultado.append({

            "id": identificador.id,

            "tipo": identificador.tipo,

            "numero": identificador.numero,

            "vigente": identificador.vigente,

            "origen": identificador.origen
        })

    return resultado


# ============================================================
# 6. CONSULTAR APLICACIONES
# ============================================================

def obtener_aplicaciones(paciente_id, db: Session):
    """
    Obtiene todas las aplicaciones de vacunas
    registradas para un paciente.

    Incluye las aplicaciones anuladas,
    pero las identifica claramente.

    No inventa fechas de vacunación.
    """

    aplicaciones = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.paciente_id == paciente_id
        )
        .order_by(
            Aplicacion.id
        )
        .all()
    )

    resultado = []

    for aplicacion in aplicaciones:

        # ----------------------------------------------------
        # OBTENER VACUNA RELACIONADA
        # ----------------------------------------------------

        vacuna = aplicacion.vacuna

        # Si existe una aplicación sin vacuna relacionada,
        # evitamos que el endpoint falle.

        if vacuna is None:

            codigo_vacuna = None
            nombre_vacuna = None

        else:

            codigo_vacuna = vacuna.codigo
            nombre_vacuna = vacuna.nombre

        # ----------------------------------------------------
        # IDENTIFICAR ESTADO DEL REGISTRO
        # ----------------------------------------------------

        if aplicacion.anulada:

            estado_registro = "anulada"

        elif aplicacion.fecha_aplicacion is None:

            estado_registro = "registrada_sin_fecha"

        else:

            estado_registro = "registrada_con_fecha"

        # ----------------------------------------------------
        # PREPARAR INFORMACIÓN
        # ----------------------------------------------------

        resultado.append({

            "id": aplicacion.id,

            "vacuna_id": aplicacion.vacuna_id,

            "codigo_vacuna": codigo_vacuna,

            "nombre_vacuna": nombre_vacuna,

            "fecha_aplicacion": convertir_fecha(
                aplicacion.fecha_aplicacion
            ),

            "fecha_confirmada": (
                aplicacion.fecha_confirmada
            ),

            "lote": aplicacion.lote,

            "laboratorio": aplicacion.laboratorio,

            "aplicada_por": aplicacion.aplicada_por,

            "origen": aplicacion.origen,

            "anulada": aplicacion.anulada,

            "motivo_anulacion": (
                aplicacion.motivo_anulacion
            ),

            "estado_registro": estado_registro
        })

    return resultado


# ============================================================
# 7. CALCULAR RESUMEN DEL HISTORIAL
# ============================================================

def calcular_resumen(aplicaciones):
    """
    Cuenta los registros del historial.

    Diferencia entre:
    - Registros no anulados.
    - Registros anulados.
    - Registros con fecha.
    - Registros sin fecha.

    Estos conteos NO indican si el esquema
    de vacunación está completo.
    """

    total_registros = len(aplicaciones)

    registros_no_anulados = 0

    registros_anulados = 0

    registros_con_fecha = 0

    registros_sin_fecha = 0

    for aplicacion in aplicaciones:

        # ----------------------------------------------------
        # REGISTROS ANULADOS
        # ----------------------------------------------------

        if aplicacion["anulada"]:

            registros_anulados += 1

            # No incluimos registros anulados
            # en los conteos de fechas vigentes.

            continue

        # ----------------------------------------------------
        # REGISTROS NO ANULADOS
        # ----------------------------------------------------

        registros_no_anulados += 1

        # ----------------------------------------------------
        # REVISAR FECHA
        # ----------------------------------------------------

        if aplicacion["fecha_aplicacion"] is None:

            registros_sin_fecha += 1

        else:

            registros_con_fecha += 1

    return {

        "total_registros": total_registros,

        "registros_no_anulados": (
            registros_no_anulados
        ),

        "registros_anulados": (
            registros_anulados
        ),

        "registros_con_fecha": (
            registros_con_fecha
        ),

        "registros_sin_fecha": (
            registros_sin_fecha
        )
    }


# ============================================================
# 8. CONSULTAR HISTORIAL COMPLETO
# ============================================================

# ENDPOINT:
# GET /historial/paciente/1

@router.get("/paciente/{paciente_id}")
def consultar_historial(
    paciente_id: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve:
    - Datos generales del paciente.
    - Identificadores.
    - Aplicaciones registradas.
    - Resumen del historial.
    """

    # --------------------------------------------------------
    # BUSCAR PACIENTE
    # --------------------------------------------------------

    paciente = db.get(
        Paciente,
        paciente_id
    )

    # --------------------------------------------------------
    # COMPROBAR EXISTENCIA
    # --------------------------------------------------------

    if paciente is None:

        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado."
        )

    # --------------------------------------------------------
    # OBTENER DATOS
    # --------------------------------------------------------

    datos_paciente = obtener_datos_paciente(
        paciente
    )

    identificadores = obtener_identificadores(
        paciente_id,
        db
    )

    aplicaciones = obtener_aplicaciones(
        paciente_id,
        db
    )

    # --------------------------------------------------------
    # CALCULAR RESUMEN
    # --------------------------------------------------------

    resumen = calcular_resumen(
        aplicaciones
    )

    # --------------------------------------------------------
    # DEVOLVER HISTORIAL COMPLETO
    # --------------------------------------------------------

    return {

        "paciente": datos_paciente,

        "identificadores": identificadores,

        "resumen": resumen,

        "aplicaciones": aplicaciones,

        "observacion": (
            "Este historial muestra registros "
            "disponibles en la base de datos. "
            "No determina si el esquema de "
            "vacunación está completo."
        )
    }


# ============================================================
# 9. CONSULTAR SOLO EL RESUMEN
# ============================================================

# ENDPOINT:
# GET /historial/paciente/1/resumen

@router.get("/paciente/{paciente_id}/resumen")
def consultar_resumen_historial(
    paciente_id: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve un resumen compacto de las aplicaciones.

    Es útil para mostrar estadísticas en
    un futuro panel de administración.
    """

    # --------------------------------------------------------
    # BUSCAR PACIENTE
    # --------------------------------------------------------

    paciente = db.get(
        Paciente,
        paciente_id
    )

    if paciente is None:

        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado."
        )

    # --------------------------------------------------------
    # CONSULTAR APLICACIONES
    # --------------------------------------------------------

    aplicaciones = obtener_aplicaciones(
        paciente_id,
        db
    )

    # --------------------------------------------------------
    # CALCULAR RESUMEN
    # --------------------------------------------------------

    resumen = calcular_resumen(
        aplicaciones
    )

    return {

        "paciente_id": paciente.id,

        "paciente": (
            f"{paciente.nombres} {paciente.apellidos}"
        ),

        "resumen": resumen,

        "observacion": (
            "Los conteos corresponden a registros, "
            "no a un esquema clínicamente completo."
        )
    }
