
# ============================================================
# ARCHIVO: backend/models/vacuna.py
#
# FUNCIÓN:
# Crear el catálogo de vacunas.
#
# Las vacunas pueden provenir de SISVACU o del
# calendario de referencia de Paraguay.
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean
)

from backend.database import Base


class Vacuna(Base):

    __tablename__ = "vacunas"

    # --------------------------------------------------------
    # IDENTIFICADOR DE LA VACUNA
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # CÓDIGO DE LA VACUNA
    # --------------------------------------------------------

    # Ejemplos:
    # BCG
    # HBRN
    # IPV-1
    # SPR-2
    #
    # unique=True evita códigos repetidos.

    codigo = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    nombre = Column(
        String(150),
        nullable=False
    )

    # --------------------------------------------------------
    # ENFERMEDADES QUE PREVIENE
    # --------------------------------------------------------

    # Este campo podrá completarse posteriormente.

    enfermedades_que_previene = Column(
        Text,
        nullable=True
    )

    # --------------------------------------------------------
    # ESTADO DE LA VACUNA
    # --------------------------------------------------------

    # Permite desactivar una vacuna del catálogo
    # sin borrar sus registros históricos.

    activa = Column(
        Boolean,
        nullable=False,
        default=True
    )
