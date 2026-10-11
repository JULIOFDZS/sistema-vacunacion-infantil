
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/usuarios.py
#
# FUNCIÓN:
# Administrar usuarios del sistema.
#
# OPERACIONES:
# - Crear usuarios.
# - Listar usuarios.
# - Consultar un usuario.
# - Modificar nombre, correo y rol.
# - Activar o desactivar cuentas.
# - Cambiar contraseñas.
#
# SEGURIDAD:
# Todas las operaciones requieren rol admin.
# ============================================================

from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict
)

from sqlalchemy import (
    select,
    func
)

from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

from backend.database import get_db

from backend.models.usuario import Usuario

from backend.dependencies.permisos import (
    permitir_roles
)

from backend.services.seguridad_service import (
    generar_hash,
    validar_password
)


# ============================================================
# 1. CONFIGURACIÓN DEL ROUTER
# ============================================================

# Todos los endpoints requieren administrador.

router = APIRouter(
    prefix="/usuarios",
    tags=["Administración de usuarios"],
    dependencies=[
        Depends(permitir_roles("admin"))
    ]
)


# ============================================================
# 2. ROLES DISPONIBLES
# ============================================================

# El administrador puede crear cuentas
# para visualizadores y operadores.
#
# No permitimos crear administradores
# adicionales mediante este endpoint.

RolCreacion = Literal[
    "visualizador",
    "operador"
]

# Para modificar usuarios permitimos
# asignar únicamente estos dos roles.
#
# Los administradores existentes no
# pueden degradarse desde esta ruta.

RolEdicion = Literal[
    "visualizador",
    "operador"
]


# ============================================================
# 3. ESQUEMAS DE ENTRADA Y SALIDA
# ============================================================

class CrearUsuario(BaseModel):

    nombre: str = Field(
        min_length=2,
        max_length=150
    )

    email: EmailStr

    password: str = Field(
        min_length=12,
        max_length=128
    )

    rol: RolCreacion


class EditarUsuario(BaseModel):

    nombre: str = Field(
        min_length=2,
        max_length=150
    )

    email: EmailStr

    rol: RolEdicion


class CambiarEstado(BaseModel):

    activo: bool


class CambiarPassword(BaseModel):

    nueva_password: str = Field(
        min_length=12,
        max_length=128
    )


class UsuarioRespuesta(BaseModel):

    id: int

    nombre: str

    email: EmailStr

    rol: str

    activo: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# 4. FUNCIÓN PARA NORMALIZAR CORREOS
# ============================================================

def normalizar_email(email: str):

    return email.strip().lower()


# ============================================================
# 5. FUNCIÓN PARA BUSCAR USUARIOS
# ============================================================

def obtener_usuario_o_404(
    usuario_id: int,
    db: Session
):

    usuario = db.get(
        Usuario,
        usuario_id
    )

    if usuario is None:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )

    return usuario


# ============================================================
# 6. CREAR USUARIO
# ============================================================

@router.post(
    "/",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear_usuario(
    datos: CrearUsuario,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # VALIDAR NOMBRE
    # --------------------------------------------------------

    nombre = datos.nombre.strip()

    if len(nombre) < 2:

        raise HTTPException(
            status_code=422,
            detail="El nombre es demasiado corto."
        )

    # --------------------------------------------------------
    # NORMALIZAR CORREO
    # --------------------------------------------------------

    email = normalizar_email(
        str(datos.email)
    )

    # --------------------------------------------------------
    # VERIFICAR CORREO DUPLICADO
    # --------------------------------------------------------

    existente = db.scalar(
        select(Usuario).where(
            Usuario.email == email
        )
    )

    if existente:

        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado."
        )

    # --------------------------------------------------------
    # VALIDAR CONTRASEÑA
    # --------------------------------------------------------

    valido, mensaje = validar_password(
        datos.password
    )

    if not valido:

        raise HTTPException(
            status_code=422,
            detail=mensaje
        )

    # --------------------------------------------------------
    # CREAR USUARIO
    # --------------------------------------------------------

    usuario = Usuario(

        nombre=nombre,

        email=email,

        password_hash=generar_hash(
            datos.password
        ),

        rol=datos.rol,

        activo=True
    )

    # --------------------------------------------------------
    # GUARDAR EN SQLITE
    # --------------------------------------------------------

    try:

        db.add(usuario)

        db.commit()

        db.refresh(usuario)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "No se pudo guardar el usuario. "
                "Verifica el correo."
            )
        )

    return usuario


# ============================================================
# 7. LISTAR USUARIOS
# ============================================================

@router.get(
    "/",
    response_model=list[UsuarioRespuesta]
)
def listar_usuarios(
    db: Session = Depends(get_db)
):

    usuarios = db.scalars(
        select(Usuario).order_by(
            Usuario.id
        )
    ).all()

    return usuarios


# ============================================================
# 8. CONSULTAR USUARIO
# ============================================================

@router.get(
    "/{usuario_id}",
    response_model=UsuarioRespuesta
)
def consultar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):

    return obtener_usuario_o_404(
        usuario_id,
        db
    )


# ============================================================
# 9. MODIFICAR USUARIO
# ============================================================

@router.put(
    "/{usuario_id}",
    response_model=UsuarioRespuesta
)
def editar_usuario(
    usuario_id: int,
    datos: EditarUsuario,
    db: Session = Depends(get_db)
):

    usuario = obtener_usuario_o_404(
        usuario_id,
        db
    )

    # --------------------------------------------------------
    # PROTEGER CUENTAS ADMINISTRADORAS
    # --------------------------------------------------------

    if usuario.rol == "admin":

        raise HTTPException(
            status_code=403,
            detail=(
                "Las cuentas administradoras "
                "no pueden modificarse desde "
                "este endpoint."
            )
        )

    nombre = datos.nombre.strip()

    if len(nombre) < 2:

        raise HTTPException(
            status_code=422,
            detail="El nombre es demasiado corto."
        )

    email = normalizar_email(
        str(datos.email)
    )

    # --------------------------------------------------------
    # COMPROBAR QUE EL CORREO NO PERTENEZCA
    # A OTRO USUARIO
    # --------------------------------------------------------

    existente = db.scalar(
        select(Usuario).where(
            Usuario.email == email,
            Usuario.id != usuario_id
        )
    )

    if existente:

        raise HTTPException(
            status_code=409,
            detail="El correo ya pertenece a otro usuario."
        )

    # --------------------------------------------------------
    # ACTUALIZAR DATOS
    # --------------------------------------------------------

    usuario.nombre = nombre

    usuario.email = email

    usuario.rol = datos.rol

    try:

        db.commit()

        db.refresh(usuario)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="No se pudo actualizar el usuario."
        )

    return usuario


# ============================================================
# 10. ACTIVAR O DESACTIVAR USUARIO
# ============================================================

@router.put(
    "/{usuario_id}/estado",
    response_model=UsuarioRespuesta
)
def cambiar_estado_usuario(
    usuario_id: int,
    datos: CambiarEstado,
    db: Session = Depends(get_db)
):

    usuario = obtener_usuario_o_404(
        usuario_id,
        db
    )

    # --------------------------------------------------------
    # NO PERMITIR DESACTIVAR ADMINISTRADORES
    # --------------------------------------------------------

    if usuario.rol == "admin":

        raise HTTPException(
            status_code=403,
            detail=(
                "No se puede cambiar el estado "
                "de una cuenta administradora "
                "desde este endpoint."
            )
        )

    usuario.activo = datos.activo

    db.commit()

    db.refresh(usuario)

    return usuario


# ============================================================
# 11. CAMBIAR CONTRASEÑA
# ============================================================

@router.put(
    "/{usuario_id}/password"
)
def cambiar_password_usuario(
    usuario_id: int,
    datos: CambiarPassword,
    db: Session = Depends(get_db)
):

    usuario = obtener_usuario_o_404(
        usuario_id,
        db
    )

    # --------------------------------------------------------
    # PROTEGER CONTRASEÑA DEL ADMINISTRADOR
    # --------------------------------------------------------

    if usuario.rol == "admin":

        raise HTTPException(
            status_code=403,
            detail=(
                "La contraseña de un administrador "
                "no puede cambiarse desde esta ruta."
            )
        )

    # --------------------------------------------------------
    # VALIDAR NUEVA CONTRASEÑA
    # --------------------------------------------------------

    valido, mensaje = validar_password(
        datos.nueva_password
    )

    if not valido:

        raise HTTPException(
            status_code=422,
            detail=mensaje
        )

    # --------------------------------------------------------
    # GENERAR NUEVO HASH
    # --------------------------------------------------------

    usuario.password_hash = generar_hash(
        datos.nueva_password
    )

    db.commit()

    return {
        "mensaje": (
            "Contraseña actualizada correctamente."
        )
    }
