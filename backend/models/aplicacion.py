
# ============================================================
# ARCHIVO: backend/models/aplicacion.py
#
# FUNCIÓN:
# Registrar las aplicaciones de vacunas de cada paciente.
#
# Relaciona:
# PACIENTE + VACUNA
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from backend.database import Base


class Aplicacion(Base):

    __tablename__ = "aplicaciones"

    # --------------------------------------------------------
    # IDENTIFICADOR DE LA APLICACIÓN
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # PACIENTE
    # --------------------------------------------------------

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # VACUNA
    # --------------------------------------------------------

    vacuna_id = Column(
        Integer,
        ForeignKey("vacunas.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # FECHA DE APLICACIÓN
    # --------------------------------------------------------

    # Puede ser NULL porque el Excel SISVACU
    # no incluye la fecha individual de cada dosis.

    fecha_aplicacion = Column(
        Date,
        nullable=True
    )

    # Indica si la fecha fue verificada.

    fecha_confirmada = Column(
        Boolean,
        nullable=False,
        default=False
    )

    # --------------------------------------------------------
    # DATOS ADICIONALES
    # --------------------------------------------------------

    lote = Column(
        String(100),
        nullable=True
    )

    laboratorio = Column(
        String(150),
        nullable=True
    )

    aplicada_por = Column(
        String(150),
        nullable=True
    )

    # --------------------------------------------------------
    # ORIGEN DEL REGISTRO
    # --------------------------------------------------------

    # Ejemplos:
    # SISVACU
    # manual

    origen = Column(
        String(30),
        nullable=False,
        default="manual"
    )

    # --------------------------------------------------------
    # ANULACIÓN
    # --------------------------------------------------------

    # Permite marcar un registro como anulado.

    anulada = Column(
        Boolean,
        nullable=False,
        default=False
    )

    motivo_anulacion = Column(
        String(255),
        nullable=True
    )

    creado_en = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    # --------------------------------------------------------
    # RELACIONES
    # --------------------------------------------------------

    paciente = relationship(
        "Paciente",
        back_populates="aplicaciones"
    )

    vacuna = relationship(
        "Vacuna"
    )

    # --------------------------------------------------------
    # RESTRICCIÓN DE DUPLICADOS
    # --------------------------------------------------------

    # En la versión actual, cada código de vacuna
    # importado representa una dosis específica.
    #
    # Por eso evitamos registrar dos veces el mismo
    # código para el mismo paciente.
    #
    # Si posteriormente permitimos aplicaciones
    # repetidas del mismo código, revisaremos
    # esta restricción.

    __table_args__ = (
        UniqueConstraint(
            "paciente_id",
            "vacuna_id",
            name="uq_paciente_vacuna"
        ),
    )
