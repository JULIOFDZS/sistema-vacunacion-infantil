
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: scripts/restablecer_admin.py
#
# OBJETIVO:
# Restablecer la contraseña de un administrador existente
# sin eliminar usuarios ni otros datos.
# ============================================================

from getpass import getpass

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.usuario import Usuario
from backend.services.seguridad_service import (
    generar_hash,
    validar_password
)


def restablecer_admin():

    db = SessionLocal()

    try:
        # Buscar los administradores existentes.
        administradores = db.scalars(
            select(Usuario).where(
                Usuario.rol == "admin"
            )
        ).all()

        if not administradores:
            print("No existe ningún administrador.")
            return

        print("\nADMINISTRADORES ENCONTRADOS")

        for usuario in administradores:
            print(
                f"ID: {usuario.id} | "
                f"Correo: {usuario.email} | "
                f"Activo: {usuario.activo}"
            )

        # Solicitar el ID para evitar cambiar otra cuenta.
        try:
            usuario_id = int(
                input("\nID del administrador: ").strip()
            )
        except ValueError:
            print("El ID debe ser un número.")
            return

        usuario = next(
            (
                admin for admin in administradores
                if admin.id == usuario_id
            ),
            None
        )

        if usuario is None:
            print("El ID no corresponde a un administrador.")
            return

        if not usuario.activo:
            print(
                "La cuenta está desactivada. "
                "No se cambiará su contraseña."
            )
            return

        # La contraseña no se muestra en pantalla.
        nueva_password = getpass(
            "\nNueva contraseña: "
        )

        confirmar_password = getpass(
            "Confirmar contraseña: "
        )

        if nueva_password != confirmar_password:
            print("Las contraseñas no coinciden.")
            return

        # Aplicar las mismas reglas del sistema.
        validar_password(nueva_password)

        confirmacion = input(
            "\nEscribe CONFIRMAR para guardar: "
        ).strip()

        if confirmacion != "CONFIRMAR":
            print("Operación cancelada.")
            return

        # Guardar solamente el nuevo hash.
        usuario.password_hash = generar_hash(
            nueva_password
        )

        db.commit()

        print("\nCONTRASEÑA ACTUALIZADA CORRECTAMENTE")
        print(f"Usuario: {usuario.email}")

    except Exception as error:
        db.rollback()
        print(f"\nError: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    restablecer_admin()
