
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/models/usuario.py
#
# FUNCIÓN:
# Definir los usuarios que pueden acceder al sistema.
#
# ROLES:
# - admin
# - visualizador
# - operador
#
# SEGURIDAD:
# Nunca guardamos contraseñas en texto plano.
# ============================================================

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    CheckConstraint
)

from backend.database import Base


# ============================================================
# 1. FUNCIÓN PARA OBTENER FECHA ACTUAL
# ============================================================

def fecha_actual_utc():
    """
    Devuelve la fecha y hora actual en UTC.

    SQLite almacena DateTime sin zona horaria,
    por lo que usamos UTC de forma consistente.
    """

    return datetime.now(timezone.utc).replace(
        tzinfo=None
    )


# ============================================================
# 2. MODELO USUARIO
# ============================================================

class Usuario(Base):

    # Nombre de la tabla en SQLite.

    __tablename__ = "usuarios"

    # --------------------------------------------------------
    # IDENTIFICADOR
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # NOMBRE COMPLETO
    # --------------------------------------------------------

    nombre = Column(
        String(150),
        nullable=False
    )

    # --------------------------------------------------------
    # CORREO ELECTRÓNICO
    # --------------------------------------------------------

    # El correo será utilizado para iniciar sesión.

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # --------------------------------------------------------
    # CONTRASEÑA PROTEGIDA
    # --------------------------------------------------------

    # Solo se almacena el hash.
    # Nunca la contraseña original.

    password_hash = Column(
        String(255),
        nullable=False
    )

    # --------------------------------------------------------
    # ROL DEL USUARIO
    # --------------------------------------------------------

    # Roles disponibles:
    #
    # admin
    # visualizador
    # operador

    rol = Column(
        String(20),
        nullable=False,
        default="visualizador"
    )

    # --------------------------------------------------------
    # ESTADO DE LA CUENTA
    # --------------------------------------------------------

    # True  = cuenta habilitada.
    # False = cuenta deshabilitada.

    activo = Column(
        Boolean,
        nullable=False,
        default=True
    )

    # --------------------------------------------------------
    # FECHA DE CREACIÓN
    # --------------------------------------------------------

    creado_en = Column(
        DateTime,
        nullable=False,
        default=fecha_actual_utc
    )

    # --------------------------------------------------------
    # FECHA DE ACTUALIZACIÓN
    # --------------------------------------------------------

    actualizado_en = Column(
        DateTime,
        nullable=False,
        default=fecha_actual_utc,
        onupdate=fecha_actual_utc
    )

    # --------------------------------------------------------
    # VALIDACIÓN DEL ROL EN SQLITE
    # --------------------------------------------------------

    __table_args__ = (

        CheckConstraint(
            "rol IN ('admin', 'visualizador', 'operador')",
            name="ck_usuarios_rol"
        ),

    )
