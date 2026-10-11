
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/services/calendario_paraguay_2026.py
#
# FUNCIÓN:
# Almacenar las reglas preliminares del calendario
# de vacunación de Paraguay 2026.
#
# IMPORTANTE:
# Este catálogo es una referencia de trabajo.
# No debe utilizarse todavía para emitir alertas
# clínicas ni determinar atrasos de vacunación.
# ============================================================


# ============================================================
# 1. ESTRUCTURA DE CADA REGLA
# ============================================================

# Cada elemento tiene cinco valores:
#
# (
#     codigo_dosis,
#     nombre_dosis,
#     edad_recomendada_meses,
#     numero_dosis,
#     tipo
# )
#
# Ejemplo:
#
# ("ROTA-1", "Rotavirus - primera dosis", 2, 1, "primaria")
#
# Significa:
# - Código: ROTA-1
# - Nombre: Rotavirus - primera dosis
# - Edad de referencia: 2 meses
# - Número de dosis: 1
# - Tipo: primaria
#
# NOTA:
# Las edades aquí registradas son referencias
# preliminares, no reglas clínicas definitivas.


# ============================================================
# 2. CALENDARIO PRELIMINAR 2026
# ============================================================

CALENDARIO_2026 = [

    # --------------------------------------------------------
    # RECIÉN NACIDO
    # --------------------------------------------------------

    (
        "BCG",
        "BCG",
        0,
        1,
        "unica"
    ),

    (
        "HEPB-RN",
        "Hepatitis B - recién nacido",
        0,
        1,
        "unica"
    ),

    # --------------------------------------------------------
    # 2 MESES
    # --------------------------------------------------------

    (
        "ROTA-1",
        "Rotavirus - primera dosis",
        2,
        1,
        "primaria"
    ),

    (
        "HEXA-1",
        "Hexavalente - primera dosis",
        2,
        1,
        "primaria"
    ),

    (
        "NEUMO13-1",
        "Neumococo 13 - primera dosis",
        2,
        1,
        "primaria"
    ),

    # --------------------------------------------------------
    # 4 MESES
    # --------------------------------------------------------

    (
        "ROTA-2",
        "Rotavirus - segunda dosis",
        4,
        2,
        "primaria"
    ),

    (
        "HEXA-2",
        "Hexavalente - segunda dosis",
        4,
        2,
        "primaria"
    ),

    (
        "NEUMO13-2",
        "Neumococo 13 - segunda dosis",
        4,
        2,
        "primaria"
    ),

    # --------------------------------------------------------
    # 6 MESES
    # --------------------------------------------------------

    (
        "HEXA-3",
        "Hexavalente - tercera dosis",
        6,
        3,
        "primaria"
    ),

    # --------------------------------------------------------
    # 12 MESES
    # --------------------------------------------------------

    (
        "NEUMO13-3",
        "Neumococo 13 - dosis posterior",
        12,
        3,
        "refuerzo"
    ),

    (
        "SPR-1",
        "SPR - primera dosis",
        12,
        1,
        "primaria"
    ),

    (
        "AA",
        "Fiebre amarilla",
        12,
        1,
        "unica"
    ),

    # --------------------------------------------------------
    # 15 MESES
    # --------------------------------------------------------

    (
        "VVZ-1",
        "Varicela - primera dosis",
        15,
        1,
        "primaria"
    ),

    (
        "HEPA-1",
        "Hepatitis A",
        15,
        1,
        "primaria"
    ),

    # --------------------------------------------------------
    # 18 MESES
    # --------------------------------------------------------

    (
        "HEXA-4",
        "Hexavalente - dosis posterior",
        18,
        4,
        "refuerzo"
    ),

    (
        "SPR-2",
        "SPR - segunda dosis",
        18,
        2,
        "primaria"
    ),

    # --------------------------------------------------------
    # 4 AÑOS = 48 MESES
    # --------------------------------------------------------

    (
        "IPV-REF",
        "IPV - refuerzo",
        48,
        1,
        "refuerzo"
    ),

    (
        "DPT-REF",
        "DPT - refuerzo",
        48,
        1,
        "refuerzo"
    ),

    # --------------------------------------------------------
    # 5 AÑOS = 60 MESES
    # --------------------------------------------------------

    (
        "VVZ-2",
        "Varicela - segunda dosis",
        60,
        2,
        "refuerzo"
    )

]


# ============================================================
# 3. OBSERVACIÓN IMPORTANTE
# ============================================================

# La vacunación contra influenza no está representada
# mediante una única regla fija porque requiere
# considerar antecedentes y recomendaciones vigentes.
#
# También debemos verificar:
# - Cambios históricos del calendario.
# - Cohorte de nacimiento del paciente.
# - Equivalencias entre códigos SISVACU y calendario.
# - Esquemas de recuperación.
#
# Por ahora solo almacenamos referencias.
