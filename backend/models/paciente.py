
# ============================================================
# ARCHIVO: backend/models/paciente.py
#
# FUNCIÓN:
# Definir la tabla de pacientes.
#
# Cada registro representa a un niño que recibe
# seguimiento de vacunación.
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    DateTime
)

from sqlalchemy.orm import relationship

from backend.database import Base


# ============================================================
# MODELO PACIENTE
# ============================================================

class Paciente(Base):

    # Nombre de la tabla dentro de SQLite.
    __tablename__ = "pacientes"

    # --------------------------------------------------------
    # IDENTIFICADOR INTERNO
    # --------------------------------------------------------

    # Es único para cada paciente.
    # No representa necesariamente su cédula.

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # DATOS PERSONALES
    # --------------------------------------------------------

    nombres = Column(
        String(100),
        nullable=False
    )

    apellidos = Column(
        String(100),
        nullable=False
    )

    # Nombre normalizado para facilitar búsquedas.
    #
    # Ejemplo:
    # "José Pérez" -> "JOSE PEREZ"

    nombre_busqueda = Column(
        String(220),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # FECHA DE NACIMIENTO
    # --------------------------------------------------------

    # Puede estar vacía porque el Excel SISVACU
    # utilizado no contiene esta información.

    fecha_nacimiento = Column(
        Date,
        nullable=True
    )

    # Indica de dónde obtuvimos la fecha.
    #
    # Ejemplos:
    # manual
    # documento
    # registro_clinico

    origen_fecha_nacimiento = Column(
        String(30),
        nullable=True
    )

    # Edad informada por SISVACU.
    #
    # No reemplaza a la fecha de nacimiento.

    edad_reportada_anios = Column(
        Integer,
        nullable=True
    )

    sexo = Column(
        String(20),
        nullable=True
    )

    # --------------------------------------------------------
    # INFORMACIÓN DE NACIMIENTO
    # --------------------------------------------------------

    # 1 = nacimiento prematuro
    # 0 = no prematuro
    # NULL = información desconocida

    nacimiento_prematuro = Column(
        Integer,
        nullable=True
    )

    semanas_gestacion = Column(
        Integer,
        nullable=True
    )

    peso_nacimiento_gr = Column(
        Integer,
        nullable=True
    )

    # --------------------------------------------------------
    # ESTADO DEL PACIENTE
    # --------------------------------------------------------

    estado = Column(
        String(30),
        nullable=False,
        default="activo"
    )

    # Indica si la ficha tiene información mínima
    # o si fue completada posteriormente.

    completitud = Column(
        String(30),
        nullable=False,
        default="minimo"
    )

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

    actualizado_en = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

    # --------------------------------------------------------
    # RELACIÓN CON IDENTIFICADORES
    # --------------------------------------------------------

    # Un paciente puede tener varios identificadores.
    #
    # Ejemplos:
    # - Código temporal SISVACU.
    # - Cédula de identidad.
    #
    # back_populates conecta ambos modelos.

    identificadores = relationship(
        "IdentificadorPaciente",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )

    # --------------------------------------------------------
    # RELACIÓN CON VACUNAS APLICADAS
    # --------------------------------------------------------

    # Un paciente puede tener múltiples aplicaciones
    # de vacunas registradas.

    aplicaciones = relationship(
        "Aplicacion",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
