
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/autenticacion.py
#
# FUNCIÓN:
# Permitir inicio de sesión y consultar
# la identidad del usuario autenticado.
#
# ENDPOINTS:
# POST /auth/login
# GET  /auth/me
# GET  /auth/verificar-admin
# ============================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from backend.database import get_db

from backend.models.usuario import Usuario

from backend.services.seguridad_service import (
    verificar_password
)

from backend.services.token_service import (
    crear_token_acceso
)

from backend.dependencies.permisos import (
    obtener_usuario_actual,
    permitir_roles
)


# ============================================================
# 1. CONFIGURAR ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


# ============================================================
# 2. CONVERTIR USUARIO A JSON SEGURO
# ============================================================

def usuario_a_json(usuario):
    """
    Devuelve únicamente los datos permitidos.

    Nunca incluye password_hash.
    """

    return {

        "id": usuario.id,

        "nombre": usuario.nombre,

        "email": usuario.email,

        "rol": usuario.rol,

        "activo": usuario.activo
    }


# ============================================================
# 3. INICIAR SESIÓN
# ============================================================

@router.post("/login")
def iniciar_sesion(
    formulario: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Recibe:
    - username: correo electrónico.
    - password: contraseña.

    Devuelve:
    - access_token.
    - token_type.
    - expires_in.
    """

    # --------------------------------------------------------
    # NORMALIZAR CORREO
    # --------------------------------------------------------

    email = (
        formulario.username
        .strip()
        .lower()
    )

    # --------------------------------------------------------
    # BUSCAR USUARIO
    # --------------------------------------------------------

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.email == email
        )
        .first()
    )

    # --------------------------------------------------------
    # VALIDAR CREDENCIALES
    # --------------------------------------------------------

    if (
        usuario is None
        or not verificar_password(
            formulario.password,
            usuario.password_hash
        )
    ):

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=(
                "Correo o contraseña incorrectos."
            ),

            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # --------------------------------------------------------
    # VERIFICAR SI LA CUENTA ESTÁ ACTIVA
    # --------------------------------------------------------

    if not usuario.activo:

        raise HTTPException(
            status_code=403,
            detail="La cuenta está deshabilitada."
        )

    # --------------------------------------------------------
    # GENERAR TOKEN
    # --------------------------------------------------------

    token = crear_token_acceso(
        usuario.id
    )

    # --------------------------------------------------------
    # DEVOLVER RESULTADO
    # --------------------------------------------------------

    return {

        "access_token": token,

        "token_type": "bearer",

        "expires_in": 1800,

        "usuario": usuario_a_json(
            usuario
        )
    }


# ============================================================
# 4. CONSULTAR MI USUARIO
# ============================================================

@router.get("/me")
def consultar_mi_usuario(
    usuario: Usuario = Depends(
        obtener_usuario_actual
    )
):
    """
    Devuelve los datos del usuario autenticado.

    Requiere un token válido.
    """

    return usuario_a_json(
        usuario
    )


# ============================================================
# 5. VERIFICAR ACCESO ADMINISTRATIVO
# ============================================================

@router.get("/verificar-admin")
def verificar_administrador(
    usuario: Usuario = Depends(
        permitir_roles("admin")
    )
):
    """
    Solo permite acceder a usuarios
    con rol de administrador.
    """

    return {

        "mensaje": (
            "Acceso administrativo autorizado."
        ),

        "usuario": usuario_a_json(
            usuario
        )
    }
