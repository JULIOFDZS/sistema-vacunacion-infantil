
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/services/token_service.py
#
# FUNCIÓN:
# Crear y validar tokens JWT para la autenticación.
#
# SEGURIDAD:
# - Utiliza una clave secreta configurada externamente.
# - Los tokens tienen vencimiento.
# - No almacena contraseñas dentro del token.
# ============================================================

import os

from datetime import (
    datetime,
    timedelta,
    timezone
)

import jwt

from jwt.exceptions import InvalidTokenError


# ============================================================
# 1. CONFIGURACIÓN JWT
# ============================================================

ALGORITMO = "HS256"

# Duración del token: 30 minutos.

DURACION_TOKEN_MINUTOS = 30


# ============================================================
# 2. OBTENER CLAVE SECRETA
# ============================================================

def obtener_clave_secreta():
    """
    Obtiene la clave desde una variable de entorno.

    Nunca utiliza una clave predeterminada.
    """

    clave = os.getenv(
        "JWT_SECRET_KEY"
    )

    if not clave or len(clave) < 32:

        raise RuntimeError(
            "JWT_SECRET_KEY no está configurada "
            "o es demasiado corta. "
            "Configura una clave segura antes "
            "de iniciar sesión."
        )

    return clave


# ============================================================
# 3. CREAR TOKEN DE ACCESO
# ============================================================

def crear_token_acceso(usuario_id: int):
    """
    Genera un token JWT para un usuario.

    El token contiene:
    - sub: identificador del usuario.
    - iat: momento de emisión.
    - exp: momento de vencimiento.

    No incluimos el rol en el token porque
    consultaremos el rol actual en SQLite.
    """

    ahora = datetime.now(
        timezone.utc
    )

    vencimiento = ahora + timedelta(
        minutes=DURACION_TOKEN_MINUTOS
    )

    datos = {

        "sub": str(usuario_id),

        "iat": ahora,

        "exp": vencimiento,

        "type": "access"
    }

    token = jwt.encode(
        datos,
        obtener_clave_secreta(),
        algorithm=ALGORITMO
    )

    return token


# ============================================================
# 4. DECODIFICAR TOKEN
# ============================================================

def decodificar_token(token: str):
    """
    Verifica la firma y el vencimiento del token.

    Devuelve los datos si es válido.

    Devuelve None si es inválido o expiró.
    """

    try:

        datos = jwt.decode(
            token,
            obtener_clave_secreta(),
            algorithms=[ALGORITMO],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp"
                ]
            }
        )

        if datos.get("type") != "access":

            return None

        return datos

    except InvalidTokenError:

        return None
