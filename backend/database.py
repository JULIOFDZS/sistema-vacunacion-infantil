
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/database.py
#
# CONEXIÓN:
# Microsoft SQL Server mediante autenticación de Windows.
#
# IMPORTANTE:
# Este archivo configura la conexión, pero no migra
# automáticamente los registros existentes de SQLite.
# ============================================================

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# 1. CONFIGURACIÓN DEL SERVIDOR
# ============================================================

SERVIDOR = os.getenv(
    "SQL_SERVER",
    r".\SQLEXPRESS"
)

BASE_DATOS = os.getenv(
    "SQL_DATABASE",
    "VacunacionInfantil"
)

CONTROLADOR = os.getenv(
    "SQL_ODBC_DRIVER",
    "ODBC Driver 18 for SQL Server"
)


# ============================================================
# 2. CADENA DE CONEXIÓN
# ============================================================

DATABASE_URL = URL.create(
    "mssql+pyodbc",
    host=SERVIDOR,
    database=BASE_DATOS,
    query={
        "driver": CONTROLADOR,
        "Trusted_Connection": "yes",
        "Encrypt": "yes",
        "TrustServerCertificate": "yes"
    }
)


# ============================================================
# 3. MOTOR DE SQLALCHEMY
# ============================================================

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)


# ============================================================
# 4. SESIONES DE BASE DE DATOS
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ============================================================
# 5. CLASE BASE PARA LOS MODELOS
# ============================================================

Base = declarative_base()


# ============================================================
# 6. DEPENDENCIA PARA FASTAPI
# ============================================================

def get_db():
    """
    Abre una sesión de base de datos para cada petición
    y la cierra al finalizar.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
