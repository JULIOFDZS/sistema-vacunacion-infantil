
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/main.py
#
# FUNCIÓN:
# - Iniciar FastAPI.
# - Conectar la base de datos.
# - Registrar todos los módulos.
# - Aplicar autenticación y permisos.
# ============================================================

from fastapi import FastAPI, Depends

# ============================================================
# 1. BASE DE DATOS
# ============================================================

from backend.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# 2. IMPORTAR MODELOS
# ============================================================

from backend.models.paciente import Paciente

from backend.models.identificador import (
    IdentificadorPaciente
)

from backend.models.vacuna import Vacuna

from backend.models.aplicacion import Aplicacion

from backend.models.esquema_dosis import (
    EsquemaDosis
)

from backend.models.equivalencia_vacuna import (
    EquivalenciaVacuna
)

from backend.models.usuario import Usuario


# ============================================================
# 3. IMPORTAR ROUTERS
# ============================================================

from backend.routes.pacientes import (
    router as pacientes_router
)

from backend.routes.importaciones import (
    router as importaciones_router
)

from backend.routes.esquema import (
    router as esquema_router
)

from backend.routes.comparacion_vacunas import (
    router as comparacion_router
)

from backend.routes.equivalencias import (
    router as equivalencias_router
)

from backend.routes.historial import (
    router as historial_router
)

from backend.routes.dashboard import (
    router as dashboard_router
)

from backend.routes.autenticacion import (
    router as autenticacion_router
)

# Nuevo módulo de administración.

from backend.routes.usuarios import (
    router as usuarios_router
)


# ============================================================
# 4. SEGURIDAD
# ============================================================

from backend.dependencies.permisos import (
    comprobar_permiso_ruta
)


# ============================================================
# 5. CREAR TABLAS FALTANTES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# 6. INICIAR FASTAPI
# ============================================================

app = FastAPI(

    title="Sistema de Seguimiento de Vacunación Infantil",

    description=(
        "API de vacunación infantil con "
        "autenticación JWT y control de roles."
    ),

    version="1.0.0"
)


# ============================================================
# 7. SEGURIDAD DE MÓDULOS EXISTENTES
# ============================================================

dependencias_protegidas = [
    Depends(comprobar_permiso_ruta)
]


# ============================================================
# 8. REGISTRAR MÓDULOS PROTEGIDOS
# ============================================================

app.include_router(
    pacientes_router,
    dependencies=dependencias_protegidas
)

app.include_router(
    importaciones_router,
    dependencies=dependencias_protegidas
)

app.include_router(
    esquema_router,
    dependencies=dependencias_protegidas
)

app.include_router(
    comparacion_router,
    dependencies=dependencias_protegidas
)

app.include_router(
    equivalencias_router,
    dependencies=dependencias_protegidas
)

app.include_router(
    historial_router,
    dependencies=dependencias_protegidas
)

app.include_router(
    dashboard_router,
    dependencies=dependencias_protegidas
)


# ============================================================
# 9. AUTENTICACIÓN
# ============================================================

# /auth/login permite iniciar sesión.
# /auth/me requiere un token.
# /auth/verificar-admin requiere rol admin.

app.include_router(
    autenticacion_router
)


# ============================================================
# 10. ADMINISTRACIÓN DE USUARIOS
# ============================================================

# Este router ya incluye la dependencia:
#
# Depends(permitir_roles("admin"))
#
# Por eso no necesita la matriz de permisos
# de los otros módulos.

app.include_router(
    usuarios_router
)


# ============================================================
# 11. RUTA PRINCIPAL
# ============================================================

@app.get("/")
def inicio():

    return {

        "mensaje": (
            "Sistema de vacunación funcionando"
        ),

        "estado": "OK"
    }


# ============================================================
# 12. ESTADO DEL SISTEMA
# ============================================================

@app.get("/estado")
def estado():

    return {

        "servidor": "activo",

        "autenticacion": "JWT",

        "roles": [
            "admin",
            "visualizador",
            "operador"
        ],

        "modulos": [
            "pacientes",
            "importaciones",
            "esquema",
            "comparacion",
            "equivalencias",
            "historial",
            "dashboard",
            "usuarios"
        ]
    }
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)