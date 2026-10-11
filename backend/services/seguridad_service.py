
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/services/seguridad_service.py
#
# FUNCIÓN:
# Crear y verificar hashes de contraseñas.
#
# UTILIZAMOS:
# Argon2 mediante pwdlib.
#
# IMPORTANTE:
# Este archivo no guarda usuarios.
# Solamente proporciona funciones de seguridad.
# ============================================================

from pwdlib import PasswordHash


# ============================================================
# 1. CONFIGURAR HASH DE CONTRASEÑAS
# ============================================================

# recommended() utiliza una configuración moderna
# para proteger las contraseñas.

password_hash = PasswordHash.recommended()


# ============================================================
# 2. DEFINIR ROLES DISPONIBLES
# ============================================================

ROL_ADMIN = "admin"

ROL_VISUALIZADOR = "visualizador"

ROL_OPERADOR = "operador"

ROLES_VALIDOS = {
    ROL_ADMIN,
    ROL_VISUALIZADOR,
    ROL_OPERADOR
}


# ============================================================
# 3. VALIDAR CONTRASEÑA
# ============================================================

def validar_password(password: str):
    """
    Comprueba los requisitos mínimos de contraseña.

    Requisitos:
    - Al menos 12 caracteres.
    - Máximo 128 caracteres.
    - No puede contener solo espacios.

    Devuelve:
    (True, mensaje) o (False, mensaje)
    """

    if not isinstance(password, str):

        return (
            False,
            "La contraseña debe ser texto."
        )

    if len(password) < 12:

        return (
            False,
            "La contraseña debe tener al menos 12 caracteres."
        )

    if len(password) > 128:

        return (
            False,
            "La contraseña no puede superar 128 caracteres."
        )

    if not password.strip():

        return (
            False,
            "La contraseña no puede estar vacía."
        )

    return (
        True,
        "Contraseña válida."
    )


# ============================================================
# 4. GENERAR HASH
# ============================================================

def generar_hash(password: str):
    """
    Recibe una contraseña original y devuelve
    su hash seguro.

    Ejemplo:
    contraseña original -> hash Argon2

    Nunca se debe imprimir ni registrar
    la contraseña original.
    """

    valido, mensaje = validar_password(
        password
    )

    if not valido:

        raise ValueError(
            mensaje
        )

    return password_hash.hash(
        password
    )


# ============================================================
# 5. VERIFICAR CONTRASEÑA
# ============================================================

def verificar_password(
    password: str,
    hash_guardado: str
):
    """
    Comprueba si una contraseña coincide
    con el hash almacenado en SQLite.

    Devuelve:
    True o False.
    """

    if not password or not hash_guardado:

        return False

    try:

        return password_hash.verify(
            password,
            hash_guardado
        )

    except (ValueError, TypeError):

        return False


# ============================================================
# 6. VALIDAR ROL
# ============================================================

def validar_rol(rol: str):
    """
    Comprueba si un rol está permitido.
    """

    return rol in ROLES_VALIDOS
