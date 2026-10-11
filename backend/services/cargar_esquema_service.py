
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/services/cargar_esquema_service.py
#
# FUNCIÓN:
# Guardar las reglas del calendario preliminar 2026
# en nuestra base de datos SQLite.
#
# OPERACIONES:
# 1. Leer las reglas del calendario.
# 2. Buscar las vacunas existentes.
# 3. Crear vacunas faltantes.
# 4. Buscar reglas existentes.
# 5. Crear reglas faltantes.
# 6. Evitar duplicados.
#
# IMPORTANTE:
# Las nuevas reglas se crean INACTIVAS.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS Y MODELOS
# ============================================================

from sqlalchemy.orm import Session

# Modelo del catálogo de vacunas.

from backend.models.vacuna import Vacuna

# Modelo de reglas de vacunación.

from backend.models.esquema_dosis import EsquemaDosis

# Lista de reglas preliminares.

from backend.services.calendario_paraguay_2026 import (
    CALENDARIO_2026
)


# ============================================================
# 2. FUNCIÓN PARA CARGAR CALENDARIO
# ============================================================

def cargar_calendario_2026(db: Session):
    """
    Guarda las reglas preliminares del calendario 2026.

    Si la vacuna existe, la reutiliza.

    Si la regla existe, no la duplica.

    Las reglas nuevas quedan inactivas.

    Devuelve un resumen de la operación.
    """

    # --------------------------------------------------------
    # CONTADORES
    # --------------------------------------------------------

    vacunas_creadas = 0

    reglas_creadas = 0

    reglas_existentes = 0

    # --------------------------------------------------------
    # RECORRER CALENDARIO
    # --------------------------------------------------------

    try:

        for (
            codigo,
            nombre,
            edad,
            numero_dosis,
            tipo
        ) in CALENDARIO_2026:

            # =================================================
            # BUSCAR VACUNA
            # =================================================

            vacuna = (
                db.query(Vacuna)
                .filter(
                    Vacuna.codigo == codigo
                )
                .first()
            )

            # -------------------------------------------------
            # CREAR VACUNA SI NO EXISTE
            # -------------------------------------------------

            if vacuna is None:

                vacuna = Vacuna(
                    codigo=codigo,
                    nombre=nombre,
                    activa=True
                )

                db.add(vacuna)

                # flush obtiene el ID antes del commit.

                db.flush()

                vacunas_creadas += 1

            # =================================================
            # BUSCAR REGLA EXISTENTE
            # =================================================

            regla = (
                db.query(EsquemaDosis)
                .filter(
                    EsquemaDosis.codigo_dosis == codigo
                )
                .first()
            )

            # -------------------------------------------------
            # SI YA EXISTE, NO DUPLICAR
            # -------------------------------------------------

            if regla is not None:

                reglas_existentes += 1

                continue

            # =================================================
            # CREAR REGLA NUEVA
            # =================================================

            nueva_regla = EsquemaDosis(

                # Vacuna asociada.
                vacuna_id=vacuna.id,

                # Código de la dosis.
                codigo_dosis=codigo,

                # Nombre de la dosis.
                nombre_dosis=nombre,

                # Número de dosis.
                numero_dosis=numero_dosis,

                # Edad mínima de referencia.
                edad_minima_meses=edad,

                # Edad recomendada de referencia.
                edad_recomendada_meses=edad,

                # No establecemos edad máxima.
                edad_maxima_meses=None,

                # Tipo de dosis.
                tipo=tipo,

                # Campo preliminar del catálogo.
                obligatoria=True,

                # IMPORTANTE:
                # No activar automáticamente.
                activa=False,

                # Motivo de la inactividad.
                observaciones=(
                    "Referencia PAI Paraguay 2026. "
                    "Pendiente de validar equivalencia "
                    "con SISVACU, cohorte y antecedentes."
                )
            )

            db.add(nueva_regla)

            reglas_creadas += 1

        # ====================================================
        # CONFIRMAR TRANSACCIÓN
        # ====================================================

        db.commit()

    except Exception:

        # Si ocurre un error, deshacer cambios.

        db.rollback()

        # Reenviar el error para que FastAPI lo registre.

        raise

    # ========================================================
    # DEVOLVER RESUMEN
    # ========================================================

    return {
        "mensaje": (
            "Calendario preliminar 2026 procesado."
        ),
        "vacunas_creadas": vacunas_creadas,
        "reglas_creadas": reglas_creadas,
        "reglas_existentes": reglas_existentes,
        "nuevas_reglas_activas": False,
        "observacion": (
            "No activar las reglas hasta validar "
            "su correspondencia con SISVACU y "
            "las recomendaciones aplicables."
        )
    }
