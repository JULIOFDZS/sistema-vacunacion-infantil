
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/services/estado_vacunacion_service.py
#
# FUNCIÓN:
# Consultar las vacunas registradas de un paciente
# y evaluar si existe información suficiente para
# comparar sus aplicaciones con el esquema.
#
# IMPORTANTE:
# El sistema no debe declarar que un niño tiene
# su vacunación completa cuando faltan datos,
# reglas validadas o equivalencias de vacunas.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

# date:
# Permite trabajar con fechas.

from datetime import date

# Session:
# Permite realizar consultas a SQLite.

from sqlalchemy.orm import Session

# Modelos de la base de datos.

from backend.models.aplicacion import Aplicacion

from backend.models.vacuna import Vacuna

from backend.models.esquema_dosis import EsquemaDosis


# ============================================================
# 2. CALCULAR EDAD EN MESES
# ============================================================

def calcular_edad_meses(paciente):
    """
    Calcula la edad del paciente en meses completos.

    Si conocemos la fecha de nacimiento:
        Calculamos los meses cumplidos.

    Si solamente conocemos la edad reportada
    por SISVACU:
        No calculamos una edad exacta.

    Devuelve:
        Número de meses o None.
    """

    # --------------------------------------------------------
    # COMPROBAR FECHA DE NACIMIENTO
    # --------------------------------------------------------

    if paciente.fecha_nacimiento is None:
        return None

    # Obtener fecha actual.

    hoy = date.today()

    # Obtener fecha de nacimiento.

    nacimiento = paciente.fecha_nacimiento

    # --------------------------------------------------------
    # VALIDAR FECHA
    # --------------------------------------------------------

    # Una fecha futura no es válida.

    if nacimiento > hoy:
        return None

    # --------------------------------------------------------
    # CALCULAR DIFERENCIA EN MESES
    # --------------------------------------------------------

    meses = (
        (hoy.year - nacimiento.year) * 12
        + (hoy.month - nacimiento.month)
    )

    # --------------------------------------------------------
    # COMPROBAR SI CUMPLIÓ EL MES
    # --------------------------------------------------------

    # Ejemplo:
    # Nació el día 20.
    # Hoy es día 10.
    #
    # Todavía no completó ese mes de edad.

    if hoy.day < nacimiento.day:
        meses -= 1

    return max(meses, 0)


# ============================================================
# 3. CONSULTAR VACUNAS REGISTRADAS
# ============================================================

def obtener_aplicadas(paciente_id, db: Session):
    """
    Obtiene las vacunas registradas para un paciente.

    Solo incluye aplicaciones no anuladas.

    Devuelve:
    - Código de la vacuna.
    - Nombre de la vacuna.
    - Fecha de aplicación.
    - Si la fecha está confirmada.
    - Origen del registro.
    """

    # --------------------------------------------------------
    # CONSULTAR APLICACIONES
    # --------------------------------------------------------

    aplicaciones = (
        db.query(Aplicacion)
        .filter(
            Aplicacion.paciente_id == paciente_id,
            Aplicacion.anulada.is_(False)
        )
        .order_by(Aplicacion.id)
        .all()
    )

    # --------------------------------------------------------
    # PREPARAR RESULTADOS
    # --------------------------------------------------------

    resultado = []

    for aplicacion in aplicaciones:

        # Obtener la vacuna relacionada.

        vacuna = aplicacion.vacuna

        # Evitar errores si falta la relación.

        if vacuna is None:
            continue

        resultado.append({

            "codigo": vacuna.codigo,

            "nombre": vacuna.nombre,

            "fecha_aplicacion": (
                aplicacion.fecha_aplicacion.isoformat()
                if aplicacion.fecha_aplicacion
                else None
            ),

            "fecha_confirmada": (
                aplicacion.fecha_confirmada
            ),

            "origen": aplicacion.origen
        })

    return resultado


# ============================================================
# 4. CONSULTAR REGLAS ACTIVAS
# ============================================================

def obtener_dosis_requeridas(edad_meses, db: Session):
    """
    Obtiene las reglas activas cuya edad mínima
    sea igual o inferior a la edad del paciente.

    Esta función consulta reglas técnicas.

    No confirma por sí sola que las dosis sean
    clínicamente exigibles para ese paciente.
    """

    # Si no conocemos la edad, no evaluamos.

    if edad_meses is None:
        return []

    reglas = (
        db.query(EsquemaDosis)
        .filter(
            EsquemaDosis.activa.is_(True),
            EsquemaDosis.obligatoria.is_(True),
            EsquemaDosis.edad_minima_meses.isnot(None),
            EsquemaDosis.edad_minima_meses <= edad_meses
        )
        .order_by(
            EsquemaDosis.edad_minima_meses,
            EsquemaDosis.id
        )
        .all()
    )

    resultado = []

    for regla in reglas:

        resultado.append({

            "codigo": regla.codigo_dosis,

            "nombre": regla.nombre_dosis,

            "edad_minima_meses": (
                regla.edad_minima_meses
            ),

            "edad_recomendada_meses": (
                regla.edad_recomendada_meses
            ),

            "tipo": regla.tipo
        })

    return resultado


# ============================================================
# 5. CALCULAR ESTADO DE VACUNACIÓN
# ============================================================

def calcular_estado_vacunacion(paciente, db: Session):
    """
    Consulta la información disponible del paciente.

    En esta etapa:
    - Muestra las aplicaciones registradas.
    - Verifica la edad disponible.
    - Verifica si hay reglas activas.
    - Evita clasificar incorrectamente como
      completo o incompleto.

    La evaluación clínica definitiva queda
    pendiente hasta validar el calendario,
    las equivalencias y los antecedentes.
    """

    # --------------------------------------------------------
    # OBTENER EDAD
    # --------------------------------------------------------

    edad_meses = calcular_edad_meses(
        paciente
    )

    # --------------------------------------------------------
    # OBTENER VACUNAS REGISTRADAS
    # --------------------------------------------------------

    aplicadas = obtener_aplicadas(
        paciente.id,
        db
    )

    # --------------------------------------------------------
    # CONTAR REGLAS ACTIVAS
    # --------------------------------------------------------

    total_reglas_activas = (
        db.query(EsquemaDosis)
        .filter(
            EsquemaDosis.activa.is_(True)
        )
        .count()
    )

    # --------------------------------------------------------
    # PREPARAR RESULTADO BASE
    # --------------------------------------------------------

    resultado = {

        "paciente_id": paciente.id,

        "paciente": (
            f"{paciente.nombres} {paciente.apellidos}"
        ),

        "edad_meses": edad_meses,

        "edad_reportada_anios": (
            paciente.edad_reportada_anios
        ),

        "total_aplicaciones_registradas": (
            len(aplicadas)
        ),

        "vacunas_aplicadas": aplicadas,

        "total_reglas_activas": total_reglas_activas,

        "dosis_requeridas": [],

        "dosis_pendientes": [],

        "estado": None,

        "evaluacion_clinica_validada": False,

        "observaciones": []
    }

    # --------------------------------------------------------
    # CASO 1: NO CONOCEMOS FECHA DE NACIMIENTO
    # --------------------------------------------------------

    if edad_meses is None:

        resultado["estado"] = (
            "edad_exacta_desconocida"
        )

        resultado["observaciones"].append(
            "No se puede calcular la edad exacta "
            "en meses porque falta una fecha de "
            "nacimiento válida."
        )

        # Aunque existan vacunas registradas,
        # no podemos calcular vencimientos.

        return resultado

    # --------------------------------------------------------
    # CASO 2: NO EXISTEN REGLAS ACTIVAS
    # --------------------------------------------------------

    if total_reglas_activas == 0:

        resultado["estado"] = (
            "sin_esquema_activo"
        )

        resultado["observaciones"].append(
            "El calendario de referencia todavía "
            "no está activado ni validado."
        )

        return resultado

    # --------------------------------------------------------
    # CASO 3: EXISTEN REGLAS ACTIVAS
    # --------------------------------------------------------

    # Consultamos las reglas cuya edad mínima
    # ya fue alcanzada por el paciente.

    reglas_por_edad = obtener_dosis_requeridas(
        edad_meses,
        db
    )

    resultado["dosis_requeridas"] = (
        reglas_por_edad
    )

    # --------------------------------------------------------
    # REVISAR COINCIDENCIAS EXACTAS DE CÓDIGOS
    # --------------------------------------------------------

    codigos_aplicados = {
        aplicacion["codigo"]
        for aplicacion in aplicadas
    }

    # Esta lista es solamente una comparación técnica.
    # No representa dosis clínicamente pendientes.

    sin_coincidencia_exacta = [

        regla

        for regla in reglas_por_edad

        if regla["codigo"] not in codigos_aplicados
    ]

    # --------------------------------------------------------
    # DEVOLVER ESTADO NO VALIDADO
    # --------------------------------------------------------

    resultado["estado"] = (
        "evaluacion_pendiente_validacion"
    )

    resultado["observaciones"].append(
        "Existen reglas activas, pero todavía "
        "deben validarse las equivalencias SISVACU, "
        "el calendario aplicable y los antecedentes "
        "antes de determinar dosis pendientes."
    )

    resultado["observaciones"].append(
        f"Hay {len(sin_coincidencia_exacta)} "
        "reglas por edad sin coincidencia exacta "
        "de código. Esto no demuestra que falten "
        "esas vacunas."
    )

    # IMPORTANTE:
    # Dejamos dosis_pendientes vacía porque aún
    # no podemos establecer pendientes clínicos.

    return resultado
