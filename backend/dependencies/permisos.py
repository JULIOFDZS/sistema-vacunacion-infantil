
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/dependencies/permisos.py
#
# FUNCIÓN:
# - Identificar al usuario autenticado.
# - Comprobar los roles.
# - Proteger las operaciones según sus permisos.
# ============================================================

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status
)

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from backend.database import get_db

from backend.models.usuario import Usuario

from backend.services.token_service import (
    decodificar_token
)


# ============================================================
# 1. AUTENTICACIÓN JWT
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# 2. ERROR DE AUTENTICACIÓN
# ============================================================

def error_autenticacion():

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación.",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )


# ============================================================
# 3. OBTENER USUARIO ACTUAL
# ============================================================

def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Comprueba:
    - Que el token sea válido.
    - Que no haya vencido.
    - Que el usuario exista.
    - Que su cuenta esté activa.
    """

    datos = decodificar_token(token)

    if datos is None:
        raise error_autenticacion()

    try:
        usuario_id = int(datos.get("sub"))

    except (TypeError, ValueError):
        raise error_autenticacion()

    usuario = db.get(
        Usuario,
        usuario_id
    )

    if usuario is None:
        raise error_autenticacion()

    if not usuario.activo:

        raise HTTPException(
            status_code=403,
            detail="La cuenta está deshabilitada."
        )

    return usuario


# ============================================================
# 4. PERMITIR ROLES ESPECÍFICOS
# ============================================================

def permitir_roles(*roles_permitidos):

    def verificar_rol(
        usuario: Usuario = Depends(
            obtener_usuario_actual
        )
    ):

        if usuario.rol not in roles_permitidos:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para "
                    "realizar esta operación."
                )
            )

        return usuario

    return verificar_rol


# ============================================================
# 5. MATRIZ DE PERMISOS POR OPERACIÓN
# ============================================================

# Todas las rutas deben figurar explícitamente aquí.
#
# Un endpoint nuevo no queda autorizado
# automáticamente por utilizar GET o POST.

PERMISOS_RUTAS = {

    # --------------------------------------------------------
    # PACIENTES
    # --------------------------------------------------------

    ("GET", "/pacientes/"): {
        "admin", "visualizador", "operador"
    },

    ("GET", "/pacientes/buscar"): {
        "admin", "visualizador", "operador"
    },

    ("GET", "/pacientes/{paciente_id}"): {
        "admin", "visualizador", "operador"
    },

    ("GET", "/pacientes/{paciente_id}/estado-vacunacion"): {
        "admin", "visualizador", "operador"
    },

    ("POST", "/pacientes/"): {
        "admin", "operador"
    },

    ("PUT", "/pacientes/{paciente_id}"): {
        "admin"
    },

    # --------------------------------------------------------
    # IMPORTACIONES SISVACU
    # --------------------------------------------------------

    ("POST", "/importaciones/sisvacu/vista-previa"): {
        "admin", "operador"
    },

    ("POST", "/importaciones/sisvacu/confirmar"): {
        "admin", "operador"
    },

    # --------------------------------------------------------
    # CALENDARIO
    # --------------------------------------------------------

    ("GET", "/esquema/"): {
        "admin", "visualizador", "operador"
    },

    ("POST", "/esquema/"): {
        "admin"
    },

    ("POST", "/esquema/cargar-inicial"): {
        "admin"
    },

    ("PUT", "/esquema/{regla_id}/estado"): {
        "admin"
    },

    # --------------------------------------------------------
    # COMPARACIÓN
    # --------------------------------------------------------

    ("GET", "/comparacion/vacunas"): {
        "admin", "visualizador", "operador"
    },

    # --------------------------------------------------------
    # EQUIVALENCIAS
    # --------------------------------------------------------

    ("GET", "/equivalencias/"): {
        "admin", "visualizador", "operador"
    },

    ("POST", "/equivalencias/"): {
        "admin"
    },

    ("PUT", "/equivalencias/{equivalencia_id}/verificar"): {
        "admin"
    },

    # --------------------------------------------------------
    # HISTORIAL
    # --------------------------------------------------------

    ("GET", "/historial/paciente/{paciente_id}"): {
        "admin", "visualizador", "operador"
    },

    ("GET", "/historial/paciente/{paciente_id}/resumen"): {
        "admin", "visualizador", "operador"
    },

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    ("GET", "/dashboard/resumen"): {
        "admin", "visualizador", "operador"
    }

}


# ============================================================
# 6. COMPROBAR PERMISO PARA CADA ENDPOINT
# ============================================================

def comprobar_permiso_ruta(
    request: Request,
    usuario: Usuario = Depends(
        obtener_usuario_actual
    )
):
    """
    Verifica el método y la ruta de la petición.

    Utilizamos la plantilla de FastAPI, por ejemplo:

    /pacientes/{paciente_id}

    En lugar de la URL concreta:

    /pacientes/15
    """

    metodo = request.method.upper()

    ruta = request.scope.get("route")

    if ruta is None:

        raise HTTPException(
            status_code=403,
            detail="Ruta no autorizada."
        )

    plantilla = ruta.path

    clave = (
        metodo,
        plantilla
    )

    roles_permitidos = PERMISOS_RUTAS.get(
        clave
    )

    # --------------------------------------------------------
    # DENEGAR RUTAS NO DECLARADAS
    # --------------------------------------------------------

    if roles_permitidos is None:

        raise HTTPException(
            status_code=403,
            detail=(
                "La operación no tiene "
                "permisos configurados."
            )
        )

    # --------------------------------------------------------
    # COMPROBAR ROL
    # --------------------------------------------------------

    if usuario.rol not in roles_permitidos:

        raise HTTPException(
            status_code=403,
            detail=(
                "Tu rol no permite realizar "
                "esta operación."
            )
        )

    return usuario
