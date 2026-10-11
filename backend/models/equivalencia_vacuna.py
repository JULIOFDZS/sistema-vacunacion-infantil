
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/models/equivalencia_vacuna.py
#
# FUNCIÓN:
# Guardar correspondencias entre códigos SISVACU
# y códigos del calendario de vacunación.
#
# IMPORTANTE:
# Una equivalencia no debe considerarse validada
# únicamente porque sus nombres sean similares.
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint
)

from backend.database import Base


# ============================================================
# MODELO DE EQUIVALENCIAS
# ============================================================

class EquivalenciaVacuna(Base):

    # Nombre de la tabla en SQLite.
    __tablename__ = "equivalencias_vacunas"

    # --------------------------------------------------------
    # IDENTIFICADOR
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # CÓDIGO ORIGINAL DE SISVACU
    # --------------------------------------------------------

    codigo_sisvacu = Column(
        String(100),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # CÓDIGO DE DOSIS DEL CALENDARIO
    # --------------------------------------------------------

    codigo_calendario = Column(
        String(100),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # ESTADO DE VALIDACIÓN
    # --------------------------------------------------------

    # Valores permitidos por nuestra API:
    #
    # pendiente
    # verificada
    #
    # Por defecto, toda equivalencia comienza
    # pendiente de revisión.

    estado = Column(
        String(20),
        nullable=False,
        default="pendiente"
    )

    # --------------------------------------------------------
    # DOCUMENTACIÓN DE LA EQUIVALENCIA
    # --------------------------------------------------------

    # Aquí podemos registrar la fuente oficial
    # o documento utilizado para verificarla.

    fuente_verificacion = Column(
        Text,
        nullable=True
    )

    # Persona que verificó la equivalencia.

    verificado_por = Column(
        String(150),
        nullable=True
    )

    # Observaciones adicionales.

    observaciones = Column(
        Text,
        nullable=True
    )

    # --------------------------------------------------------
    # FECHAS DE CONTROL
    # --------------------------------------------------------

    creado_en = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    verificado_en = Column(
        DateTime,
        nullable=True
    )

    # --------------------------------------------------------
    # EVITAR CORRESPONDENCIAS DUPLICADAS
    # --------------------------------------------------------

    # No permite registrar dos veces la misma pareja
    # de códigos.

    __table_args__ = (
        UniqueConstraint(
            "codigo_sisvacu",
            "codigo_calendario",
            name="uq_equivalencia_codigos"
        ),
    )
