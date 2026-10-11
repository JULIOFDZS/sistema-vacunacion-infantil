
# ============================================================
# ARCHIVO: backend/models/esquema_dosis.py
#
# FUNCIÓN:
# Guardar las reglas del esquema de vacunación.
#
# Ejemplo:
# Vacuna: BCG
# Edad recomendada: 0 meses
#
# Las reglas deben validarse antes de utilizarlas
# para generar alertas de vacunas pendientes.
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from backend.database import Base


class EsquemaDosis(Base):

    __tablename__ = "esquema_dosis"

    # --------------------------------------------------------
    # IDENTIFICADOR
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # VACUNA RELACIONADA
    # --------------------------------------------------------

    vacuna_id = Column(
        Integer,
        ForeignKey("vacunas.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # CÓDIGO Y NOMBRE DE LA DOSIS
    # --------------------------------------------------------

    codigo_dosis = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    nombre_dosis = Column(
        String(150),
        nullable=False
    )

    numero_dosis = Column(
        Integer,
        nullable=True
    )

    # --------------------------------------------------------
    # EDADES EN MESES
    # --------------------------------------------------------

    # Edad mínima para la dosis.
    edad_minima_meses = Column(
        Integer,
        nullable=True
    )

    # Edad recomendada por el calendario.
    edad_recomendada_meses = Column(
        Integer,
        nullable=True
    )

    # Edad máxima, cuando corresponda.
    edad_maxima_meses = Column(
        Integer,
        nullable=True
    )

    # --------------------------------------------------------
    # TIPO DE DOSIS
    # --------------------------------------------------------

    # Ejemplos:
    # primaria
    # refuerzo
    # unica

    tipo = Column(
        String(30),
        nullable=True
    )

    # --------------------------------------------------------
    # OBLIGATORIA
    # --------------------------------------------------------

    obligatoria = Column(
        Boolean,
        nullable=False,
        default=True
    )

    # --------------------------------------------------------
    # ESTADO DE LA REGLA
    # --------------------------------------------------------

    # Las reglas cargadas desde el catálogo inicial
    # permanecen inactivas hasta su validación.

    activa = Column(
        Boolean,
        nullable=False,
        default=True
    )

    # --------------------------------------------------------
    # OBSERVACIONES
    # --------------------------------------------------------

    observaciones = Column(
        Text,
        nullable=True
    )

    # --------------------------------------------------------
    # FECHA DE CREACIÓN
    # --------------------------------------------------------

    creado_en = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    # --------------------------------------------------------
    # RELACIÓN CON VACUNA
    # --------------------------------------------------------

    vacuna = relationship(
        "Vacuna"
    )
