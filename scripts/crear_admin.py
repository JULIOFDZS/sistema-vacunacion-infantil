
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: scripts/crear_admin.py
#
# FUNCIÓN:
# Crear la primera cuenta administradora del sistema.
#
# SEGURIDAD:
# - Solo funciona si no existe ningún usuario.
# - No utiliza contraseñas predeterminadas.
# - Solicita la contraseña sin mostrarla.
# - Guarda únicamente el hash de la contraseña.
#
# EJECUCIÓN:
# python -m scripts.crear_admin
# ============================================================

from getpass import getpass

from sqlalchemy import select, func

# Conexión a SQLite.

from backend.database import (
    Base,
    engine,
    SessionLocal
)

# Importamos el modelo Usuario.

from backend.models.usuario import Usuario

# Funciones de seguridad.

from backend.services.seguridad_service import (
    generar_hash,
    validar_password,
    ROL_ADMIN
)


# ============================================================
# 1. FUNCIÓN PRINCIPAL
# ============================================================

def crear_administrador():

    print()
    print("=" * 55)
    print("CREACIÓN DEL ADMINISTRADOR INICIAL")
    print("=" * 55)

    # --------------------------------------------------------
    # CREAR TABLA SI TODAVÍA NO EXISTE
    # --------------------------------------------------------

    Base.metadata.create_all(
        bind=engine
    )

    # --------------------------------------------------------
    # ABRIR SESIÓN DE SQLITE
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # COMPROBAR SI YA EXISTEN USUARIOS
        # ----------------------------------------------------

        total_usuarios = db.scalar(
            select(func.count()).select_from(Usuario)
        )

        if total_usuarios > 0:

            print()
            print(
                "No se puede crear otro administrador inicial."
            )

            print(
                "Ya existen usuarios en la base de datos."
            )

            print(
                "La administración de cuentas se hará "
                "desde el módulo protegido de usuarios."
            )

            return

        # ----------------------------------------------------
        # SOLICITAR NOMBRE
        # ----------------------------------------------------

        nombre = input(
            "Nombre del administrador: "
        ).strip()

        if not nombre:

            print("ERROR: El nombre es obligatorio.")
            return

        # ----------------------------------------------------
        # SOLICITAR CORREO
        # ----------------------------------------------------

        email = input(
            "Correo electrónico: "
        ).strip().lower()

        if (
            not email
            or "@" not in email
            or len(email) > 255
        ):

            print("ERROR: Correo electrónico no válido.")
            return

        # ----------------------------------------------------
        # SOLICITAR CONTRASEÑA
        # ----------------------------------------------------

        password = getpass(
            "Contraseña (mínimo 12 caracteres): "
        )

        # ----------------------------------------------------
        # VALIDAR CONTRASEÑA
        # ----------------------------------------------------

        valido, mensaje = validar_password(
            password
        )

        if not valido:

            print("ERROR:", mensaje)
            return

        # ----------------------------------------------------
        # CONFIRMAR CONTRASEÑA
        # ----------------------------------------------------

        confirmacion = getpass(
            "Confirmar contraseña: "
        )

        if password != confirmacion:

            print(
                "ERROR: Las contraseñas no coinciden."
            )

            return

        # ----------------------------------------------------
        # GENERAR HASH SEGURO
        # ----------------------------------------------------

        hash_seguro = generar_hash(
            password
        )

        # ----------------------------------------------------
        # CREAR ADMINISTRADOR
        # ----------------------------------------------------

        administrador = Usuario(

            nombre=nombre,

            email=email,

            password_hash=hash_seguro,

            rol=ROL_ADMIN,

            activo=True
        )

        # ----------------------------------------------------
        # GUARDAR EN SQLITE
        # ----------------------------------------------------

        db.add(administrador)

        db.commit()

        db.refresh(administrador)

        # ----------------------------------------------------
        # MOSTRAR CONFIRMACIÓN
        # ----------------------------------------------------

        print()
        print("=" * 55)

        print(
            "Administrador inicial creado correctamente."
        )

        print(
            f"ID: {administrador.id}"
        )

        print(
            f"Correo: {administrador.email}"
        )

        print(
            f"Rol: {administrador.rol}"
        )

        print("=" * 55)

        print()
        print(
            "La contraseña no se muestra ni se guarda "
            "en texto plano."
        )

    except Exception as error:

        # ----------------------------------------------------
        # REVERTIR CAMBIOS SI OCURRE UN ERROR
        # ----------------------------------------------------

        db.rollback()

        print()
        print(
            "No fue posible crear el administrador."
        )

        print(
            f"Detalle técnico: {type(error).__name__}"
        )

    finally:

        # ----------------------------------------------------
        # CERRAR SESIÓN
        # ----------------------------------------------------

        db.close()


# ============================================================
# 2. EJECUTAR SCRIPT
# ============================================================

if __name__ == "__main__":

    crear_administrador()