
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/comparacion_vacunas.py
#
# FUNCIÓN:
# Comparar los códigos de dosis registrados en SISVACU
# con las reglas de referencia del calendario.
#
# CLASIFICACIONES:
# 1. Coincidencias exactas.
# 2. Equivalencias verificadas.
# 3. Equivalencias pendientes.
# 4. Códigos sin correspondencia.
#
# IMPORTANTE:
# Este módulo es de consulta.
# NO modifica pacientes, vacunas ni equivalencias.
#
# Tampoco determina si un niño tiene vacunas
# atrasadas, completas o pendientes.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

# APIRouter:
# Permite organizar los endpoints de comparación.
#
# Depends:
# Permite utilizar la conexión a la base de datos.

from fastapi import APIRouter, Depends

# Session:
# Permite realizar consultas con SQLAlchemy.

from sqlalchemy.orm import Session

# Conexión a nuestra base de datos SQLite.

from backend.database import get_db

# Modelo de las aplicaciones registradas.

from backend.models.aplicacion import Aplicacion

# Modelo de las reglas del calendario.

from backend.models.esquema_dosis import EsquemaDosis

# Modelo de las equivalencias del Bloque 6.

from backend.models.equivalencia_vacuna import (
    EquivalenciaVacuna
)


# ============================================================
# 2. CONFIGURAR ROUTER
# ============================================================

# Todos los endpoints comenzarán con:
#
# /comparacion

router = APIRouter(
    prefix="/comparacion",
    tags=["Comparación SISVACU"]
)


# ============================================================
# 3. NORMALIZAR CÓDIGOS
# ============================================================

def normalizar_codigo(codigo):
    """
    Convierte un código a mayúsculas
    y elimina espacios al inicio y al final.

    Ejemplos:

    " bcg " -> "BCG"
    "hexa-1" -> "HEXA-1"

    IMPORTANTE:
    No elimina guiones ni modifica la estructura
    del código, porque podrían ser significativos.
    """

    if codigo is None:
        return ""

    return str(codigo).strip().upper()


# ============================================================
# 4. IDENTIFICAR ORIGEN SISVACU
# ============================================================

def es_origen_sisvacu(origen):
    """
    Comprueba si una aplicación proviene de SISVACU.

    Acepta:
    - SISVACU
    - sisvacu
    - Sisvacu
    - Valores con espacios adicionales.
    """

    if origen is None:
        return False

    return (
        str(origen).strip().upper()
        == "SISVACU"
    )


# ============================================================
# 5. ENDPOINT DE COMPARACIÓN
# ============================================================

# ENDPOINT:
# GET /comparacion/vacunas

@router.get("/vacunas")
def comparar_vacunas(
    db: Session = Depends(get_db)
):
    """
    Compara los códigos de SISVACU con el calendario.

    Devuelve:
    - Total de códigos SISVACU.
    - Total de códigos del calendario.
    - Coincidencias exactas.
    - Equivalencias verificadas.
    - Equivalencias pendientes.
    - Códigos sin correspondencia.
    - Reglas sin registros SISVACU relacionados.

    Esta comparación es informativa.
    """

    # ========================================================
    # 6. CONSULTAR REGLAS DEL CALENDARIO
    # ========================================================

    reglas = (
        db.query(EsquemaDosis)
        .all()
    )

    # --------------------------------------------------------
    # CREAR DICCIONARIO DE REGLAS
    # --------------------------------------------------------

    # Utilizamos el código de dosis como clave.
    #
    # Ejemplo:
    #
    # {
    #     "BCG": regla_BCG,
    #     "HEPB-RN": regla_hepatitis
    # }

    reglas_por_codigo = {}

    for regla in reglas:

        codigo = normalizar_codigo(
            regla.codigo_dosis
        )

        if codigo:

            reglas_por_codigo[codigo] = regla

    # Conjunto de códigos del calendario.

    codigos_calendario = set(
        reglas_por_codigo.keys()
    )

    # ========================================================
    # 7. CONSULTAR APLICACIONES REGISTRADAS
    # ========================================================

    aplicaciones = (
        db.query(Aplicacion)
        .all()
    )

    # --------------------------------------------------------
    # OBTENER CÓDIGOS IMPORTADOS DESDE SISVACU
    # --------------------------------------------------------

    codigos_sisvacu = set()

    for aplicacion in aplicaciones:

        # Ignorar aplicaciones anuladas.

        if aplicacion.anulada:
            continue

        # Ignorar registros de otros orígenes.

        if not es_origen_sisvacu(
            aplicacion.origen
        ):
            continue

        # Obtener la vacuna relacionada.

        vacuna = aplicacion.vacuna

        if vacuna is None:
            continue

        codigo = normalizar_codigo(
            vacuna.codigo
        )

        if codigo:

            codigos_sisvacu.add(
                codigo
            )

    # ========================================================
    # 8. CONSULTAR EQUIVALENCIAS REGISTRADAS
    # ========================================================

    equivalencias = (
        db.query(EquivalenciaVacuna)
        .all()
    )

    # --------------------------------------------------------
    # ORGANIZAR EQUIVALENCIAS POR CÓDIGO SISVACU
    # --------------------------------------------------------

    # Ejemplo:
    #
    # {
    #     "HBRN": [equivalencia_1],
    #     "IPV-2R": [equivalencia_2]
    # }

    equivalencias_por_codigo = {}

    for equivalencia in equivalencias:

        codigo_sisvacu = normalizar_codigo(
            equivalencia.codigo_sisvacu
        )

        if codigo_sisvacu not in equivalencias_por_codigo:

            equivalencias_por_codigo[
                codigo_sisvacu
            ] = []

        equivalencias_por_codigo[
            codigo_sisvacu
        ].append(
            equivalencia
        )

    # ========================================================
    # 9. PREPARAR RESULTADOS
    # ========================================================

    coincidencias_exactas = []

    equivalencias_verificadas = []

    equivalencias_pendientes = []

    codigos_sin_correspondencia = []

    # Códigos del calendario que tienen alguna relación
    # exacta o verificada con registros SISVACU.

    codigos_calendario_relacionados = set()

    # ========================================================
    # 10. RECORRER CÓDIGOS SISVACU
    # ========================================================

    for codigo in sorted(codigos_sisvacu):

        # ----------------------------------------------------
        # CASO A: COINCIDENCIA EXACTA
        # ----------------------------------------------------

        if codigo in codigos_calendario:

            coincidencias_exactas.append(
                codigo
            )

            codigos_calendario_relacionados.add(
                codigo
            )

        # ----------------------------------------------------
        # BUSCAR EQUIVALENCIAS DEL CÓDIGO
        # ----------------------------------------------------

        equivalencias_codigo = (
            equivalencias_por_codigo.get(
                codigo,
                []
            )
        )

        # ----------------------------------------------------
        # CONTADORES DE EQUIVALENCIAS VÁLIDAS
        # ----------------------------------------------------

        tiene_equivalencia_registrada = False

        # ----------------------------------------------------
        # REVISAR CADA EQUIVALENCIA
        # ----------------------------------------------------

        for equivalencia in equivalencias_codigo:

            codigo_calendario = normalizar_codigo(
                equivalencia.codigo_calendario
            )

            # Ignorar correspondencias que apuntan
            # a reglas inexistentes.

            if codigo_calendario not in codigos_calendario:
                continue

            tiene_equivalencia_registrada = True

            # Preparar información.

            informacion = {

                "codigo_sisvacu": codigo,

                "codigo_calendario": (
                    codigo_calendario
                ),

                "equivalencia_id": (
                    equivalencia.id
                ),

                "estado": equivalencia.estado,

                "observaciones": (
                    equivalencia.observaciones
                ),

                "fuente_verificacion": (
                    equivalencia.fuente_verificacion
                ),

                "verificado_por": (
                    equivalencia.verificado_por
                )
            }

            # ------------------------------------------------
            # EQUIVALENCIA VERIFICADA
            # ------------------------------------------------

            # Además del estado, exigimos datos
            # documentales para mostrarla como verificada.

            verificacion_documentada = (
                equivalencia.estado == "verificada"
                and bool(
                    equivalencia.fuente_verificacion
                    and equivalencia.fuente_verificacion.strip()
                )
                and bool(
                    equivalencia.verificado_por
                    and equivalencia.verificado_por.strip()
                )
            )

            if verificacion_documentada:

                equivalencias_verificadas.append(
                    informacion
                )

                codigos_calendario_relacionados.add(
                    codigo_calendario
                )

            # ------------------------------------------------
            # EQUIVALENCIA PENDIENTE
            # ------------------------------------------------

            else:

                equivalencias_pendientes.append(
                    informacion
                )

        # ----------------------------------------------------
        # CASO D: SIN CORRESPONDENCIA
        # ----------------------------------------------------

        # Si el código no coincide exactamente
        # y tampoco tiene equivalencias registradas.

        if (
            codigo not in codigos_calendario
            and not tiene_equivalencia_registrada
        ):

            codigos_sin_correspondencia.append(
                codigo
            )

    # ========================================================
    # 11. REGLAS SIN REGISTROS RELACIONADOS
    # ========================================================

    reglas_sin_registros_importados = sorted(
        codigos_calendario
        - codigos_calendario_relacionados
    )

    # ========================================================
    # 12. DEVOLVER RESULTADO FINAL
    # ========================================================

    return {

        "resumen": {

            "total_codigos_sisvacu": (
                len(codigos_sisvacu)
            ),

            "total_codigos_calendario": (
                len(codigos_calendario)
            ),

            "total_coincidencias_exactas": (
                len(coincidencias_exactas)
            ),

            "total_equivalencias_verificadas": (
                len(equivalencias_verificadas)
            ),

            "total_equivalencias_pendientes": (
                len(equivalencias_pendientes)
            ),

            "total_codigos_sin_correspondencia": (
                len(codigos_sin_correspondencia)
            )
        },

        "coincidencias_exactas": (
            coincidencias_exactas
        ),

        "equivalencias_verificadas": (
            equivalencias_verificadas
        ),

        "equivalencias_pendientes": (
            equivalencias_pendientes
        ),

        "codigos_sin_correspondencia": (
            codigos_sin_correspondencia
        ),

        "reglas_sin_registros_importados": (
            reglas_sin_registros_importados
        ),

        "advertencias": [

            "Las coincidencias exactas de códigos "
            "no garantizan equivalencia clínica.",

            "Las equivalencias pendientes no deben "
            "utilizarse para evaluar pacientes.",

            "Una equivalencia verificada requiere "
            "revisión documental y no sustituye "
            "la validación del calendario aplicable.",

            "La ausencia de un registro importado "
            "no demuestra que una dosis esté pendiente."
        ]
    }
