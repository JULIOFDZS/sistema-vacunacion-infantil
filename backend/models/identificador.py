
# ============================================================
# ARCHIVO: backend/models/identificador.py
#
# FUNCIÓN:
# Guardar los diferentes identificadores de un paciente.
#
# Ejemplos:
# - Cédula: 8841439
# - Código SISVACU: JSCG07012021
# - Identificador SISVACU: ISAIAS
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from backend.database import Base


class IdentificadorPaciente(Base):

    # Nombre de la tabla.
    __tablename__ = "identificadores_paciente"

    # --------------------------------------------------------
    # IDENTIFICADOR INTERNO
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # PACIENTE AL QUE PERTENECE
    # --------------------------------------------------------

    # ForeignKey crea la relación con pacientes.id.

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # TIPO DE IDENTIFICADOR
    # --------------------------------------------------------

    # Ejemplos:
    # cedula
    # temporal_sisvacu

    tipo = Column(
        String(50),
        nullable=False
    )

    # Número o código del documento.

    numero = Column(
        String(50),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # VIGENCIA
    # --------------------------------------------------------

    # True: identificador vigente.
    # False: identificador anterior.

    vigente = Column(
        Boolean,
        nullable=False,
        default=True
    )

    # --------------------------------------------------------
    # ORIGEN
    # --------------------------------------------------------

    # Permite saber de dónde proviene el identificador.

    origen = Column(
        String(30),
        nullable=False,
        default="manual"
    )

    fecha_registro = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    # --------------------------------------------------------
    # RELACIÓN CON PACIENTE
    # --------------------------------------------------------

    paciente = relationship(
        "Paciente",
        back_populates="identificadores"
    )

    # --------------------------------------------------------
    # EVITAR IDENTIFICADORES REPETIDOS
    # --------------------------------------------------------

    # No permite repetir la misma combinación
    # de tipo y número.

    __table_args__ = (
        UniqueConstraint(
            "tipo",
            "numero",
            name="uq_identificador_tipo_numero"
        ),
    )
