
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: scripts/crear_tablas_sqlserver.py
#
# OBJETIVO:
# Crear las tablas de SQL Server utilizando los
# modelos SQLAlchemy existentes.
#
# SEGURIDAD:
# - No elimina tablas.
# - No borra registros.
# - No modifica SQLite.
# - Se detiene si encuentra tablas existentes
#   en la base de datos de destino.
# ============================================================

from sqlalchemy import inspect

from backend.database import (
    Base,
    engine
)

# ============================================================
# 1. IMPORTAR LOS SIETE MODELOS
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
# 2. CREAR LAS TABLAS
# ============================================================

def crear_tablas():

    print("=" * 60)
    print("CREACIÓN DE TABLAS EN SQL SERVER")
    print("=" * 60)

    # --------------------------------------------------------
    # VERIFICAR QUE SEA SQL SERVER
    # --------------------------------------------------------

    if engine.dialect.name != "mssql":

        raise RuntimeError(
            "La conexión no corresponde a SQL Server."
        )

    # --------------------------------------------------------
    # VERIFICAR BASE DE DATOS DE DESTINO
    # --------------------------------------------------------

    nombre_base = engine.url.database

    if (
        not nombre_base
        or nombre_base.lower() != "vacunacioninfantil"
    ):

        raise RuntimeError(
            "La base de datos de destino no es "
            "VacunacionInfantil."
        )

    print(f"\nBase de datos: {nombre_base}")

    # --------------------------------------------------------
    # VERIFICAR SI EXISTEN TABLAS
    # --------------------------------------------------------

    inspector = inspect(engine)

    tablas_existentes = inspector.get_table_names()

    if tablas_existentes:

        print(
            "\nATENCIÓN: La base de datos ya tiene tablas."
        )

        for tabla in tablas_existentes:
            print(f"- {tabla}")

        print(
            "\nNo se realizarán cambios automáticos."
        )

        return

    # --------------------------------------------------------
    # MOSTRAR LAS TABLAS QUE SE CREARÁN
    # --------------------------------------------------------

    print("\nTablas que se crearán:")

    for tabla in Base.metadata.sorted_tables:
        print(f"- {tabla.name}")

    # --------------------------------------------------------
    # CREAR LAS TABLAS
    # --------------------------------------------------------

    print("\nCreando tablas...")

    Base.metadata.create_all(
        bind=engine
    )

    # --------------------------------------------------------
    # VERIFICAR EL RESULTADO
    # --------------------------------------------------------

    inspector = inspect(engine)

    tablas_creadas = inspector.get_table_names()

    esperadas = {
        tabla.name
        for tabla in Base.metadata.tables.values()
    }

    creadas = set(tablas_creadas)

    faltantes = esperadas - creadas

    print("\nTablas encontradas en SQL Server:")

    for tabla in sorted(tablas_creadas):
        print(f"- {tabla}")

    print("\n" + "=" * 60)

    if faltantes:

        print("FALTAN TABLAS:")

        for tabla in sorted(faltantes):
            print(f"- {tabla}")

        raise RuntimeError(
            "La creación de tablas está incompleta."
        )

    print("TABLAS CREADAS CORRECTAMENTE")
    print(f"Total: {len(esperadas)}")

    print("=" * 60)


# ============================================================
# 3. EJECUTAR
# ============================================================

if __name__ == "__main__":
    crear_tablas()
