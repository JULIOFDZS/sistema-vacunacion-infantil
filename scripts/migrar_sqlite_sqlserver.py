
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: scripts/migrar_sqlite_sqlserver.py
#
# OBJETIVO:
# Migrar todos los registros desde SQLite a SQL Server.
#
# SEGURIDAD:
# - SQLite se abre en modo solo lectura.
# - No se eliminan tablas ni registros.
# - SQL Server debe tener las tablas vacías.
# - Se conservan los ID originales.
# - Se respetan las claves foráneas.
# - Si ocurre un error, se revierte la transacción.
# ============================================================

import sqlite3

from pathlib import Path
from datetime import date, datetime, time
from urllib.parse import quote

from sqlalchemy import (
    MetaData,
    Table,
    inspect,
    select,
    func
)

from sqlalchemy.sql.sqltypes import (
    Date,
    DateTime,
    Time
)

from backend.database import engine, Base

# ============================================================
# 1. IMPORTAR TODOS LOS MODELOS
# ============================================================

from backend.models.paciente import Paciente
from backend.models.identificador import IdentificadorPaciente
from backend.models.vacuna import Vacuna
from backend.models.aplicacion import Aplicacion
from backend.models.esquema_dosis import EsquemaDosis
from backend.models.equivalencia_vacuna import EquivalenciaVacuna
from backend.models.usuario import Usuario


# ============================================================
# 2. UBICACIÓN DE SQLITE
# ============================================================

CARPETA_PROYECTO = (
    Path(__file__).resolve().parent.parent
)

RUTA_SQLITE = (
    CARPETA_PROYECTO / "vacunacion.db"
)


# ============================================================
# 3. CONEXIÓN SQLITE DE SOLO LECTURA
# ============================================================

def conectar_sqlite():

    if not RUTA_SQLITE.is_file():
        raise RuntimeError(
            f"No se encontró SQLite: {RUTA_SQLITE}"
        )

    # El modo ro evita modificar la base original.

    ruta_uri = (
        "file:"
        + quote(RUTA_SQLITE.as_posix(), safe="/:")
        + "?mode=ro"
    )

    conexion = sqlite3.connect(
        ruta_uri,
        uri=True
    )

    conexion.row_factory = sqlite3.Row

    return conexion


# ============================================================
# 4. CONSULTAS SEGURAS DE NOMBRES DE TABLA
# ============================================================

def nombre_sqlite(nombre):

    return '"' + nombre.replace('"', '""') + '"'


def contar_sqlite(conexion, nombre):

    consulta = (
        f"SELECT COUNT(*) FROM "
        f"{nombre_sqlite(nombre)}"
    )

    return conexion.execute(
        consulta
    ).fetchone()[0]


# ============================================================
# 5. CONVERTIR FECHAS PARA SQL SERVER
# ============================================================

def convertir_valor(valor, columna):

    if valor is None:
        return None

    tipo = columna.type

    if isinstance(tipo, DateTime):

        if isinstance(valor, str):
            return datetime.fromisoformat(
                valor.replace("Z", "+00:00")
            )

    elif isinstance(tipo, Date):

        if isinstance(valor, str):
            return date.fromisoformat(
                valor[:10]
            )

    elif isinstance(tipo, Time):

        if isinstance(valor, str):
            return time.fromisoformat(valor)

    return valor


# ============================================================
# 6. VALIDAR BASES Y TABLAS
# ============================================================

def validar_estructura(sqlite):

    print("=" * 65)
    print("MIGRACIÓN SQLITE A SQL SERVER")
    print("=" * 65)

    # Confirmar motor y base de destino.

    if engine.dialect.name != "mssql":
        raise RuntimeError(
            "El destino no es SQL Server."
        )

    if (
        not engine.url.database
        or engine.url.database.lower()
        != "vacunacioninfantil"
    ):
        raise RuntimeError(
            "El destino no es VacunacionInfantil."
        )

    inspector = inspect(engine)

    tablas_destino = set(
        inspector.get_table_names(schema="dbo")
    )

    tablas_origen = {
        fila[0]
        for fila in sqlite.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
    }

    tablas_modelo = [
        tabla.name
        for tabla in Base.metadata.sorted_tables
    ]

    # No migrar si falta alguna tabla.

    faltan_origen = (
        set(tablas_modelo) - tablas_origen
    )

    faltan_destino = (
        set(tablas_modelo) - tablas_destino
    )

    if faltan_origen:
        raise RuntimeError(
            "Faltan tablas en SQLite: "
            + ", ".join(sorted(faltan_origen))
        )

    if faltan_destino:
        raise RuntimeError(
            "Faltan tablas en SQL Server: "
            + ", ".join(sorted(faltan_destino))
        )

    # Evitar ignorar tablas adicionales con datos.

    adicionales = (
        tablas_origen - set(tablas_modelo)
    )

    if adicionales:
        raise RuntimeError(
            "Hay tablas adicionales en SQLite "
            "que necesitan revisión: "
            + ", ".join(sorted(adicionales))
        )

    print("\nEstructura encontrada correctamente.")

    return tablas_modelo


# ============================================================
# 7. MIGRAR REGISTROS
# ============================================================

def migrar():

    sqlite = conectar_sqlite()

    try:

        tablas_modelo = validar_estructura(
            sqlite
        )

        # Reflejar la estructura real de SQL Server.

        metadata_destino = MetaData()

        tablas_destino = {}

        for nombre in tablas_modelo:

            tablas_destino[nombre] = Table(
                nombre,
                metadata_destino,
                schema="dbo",
                autoload_with=engine
            )

        # ----------------------------------------------------
        # VALIDAR COLUMNAS
        # ----------------------------------------------------

        for nombre in tablas_modelo:

            columnas_sqlite = {
                fila[1]
                for fila in sqlite.execute(
                    f"PRAGMA table_info("
                    f"{nombre_sqlite(nombre)})"
                )
            }

            columnas_destino = {
                columna.name
                for columna
                in tablas_destino[nombre].columns
            }

            if columnas_sqlite != columnas_destino:

                raise RuntimeError(
                    f"Columnas diferentes en {nombre}. "
                    f"SQLite: {sorted(columnas_sqlite)}. "
                    f"SQL Server: "
                    f"{sorted(columnas_destino)}"
                )

        # ----------------------------------------------------
        # MOSTRAR RESUMEN DEL ORIGEN
        # ----------------------------------------------------

        print("\nRegistros encontrados en SQLite:")

        total_origen = 0

        for nombre in tablas_modelo:

            cantidad = contar_sqlite(
                sqlite,
                nombre
            )

            total_origen += cantidad

            print(
                f"  {nombre}: {cantidad}"
            )

        print(
            f"\nTotal de registros: {total_origen}"
        )

        # ----------------------------------------------------
        # INICIAR TRANSACCIÓN EN SQL SERVER
        # ----------------------------------------------------

        # Si hay un error, engine.begin() revierte
        # las inserciones realizadas en esta transacción.

        with engine.begin() as conexion:

            # ------------------------------------------------
            # COMPROBAR QUE EL DESTINO ESTÉ VACÍO
            # ------------------------------------------------

            for nombre in tablas_modelo:

                tabla = tablas_destino[nombre]

                cantidad = conexion.scalar(
                    select(func.count()).select_from(
                        tabla
                    )
                )

                if cantidad != 0:

                    raise RuntimeError(
                        f"La tabla {nombre} ya contiene "
                        f"{cantidad} registros. "
                        "Se cancela la migración."
                    )

            print(
                "\nSQL Server está vacío. "
                "Comenzando la copia..."
            )

            # ------------------------------------------------
            # INSERTAR EN ORDEN DE DEPENDENCIAS
            # ------------------------------------------------

            for nombre in tablas_modelo:

                tabla = tablas_destino[nombre]

                consulta = (
                    f"SELECT * FROM "
                    f"{nombre_sqlite(nombre)}"
                )

                cursor = sqlite.execute(
                    consulta
                )

                contador = 0

                for fila in cursor:

                    registro = {}

                    for columna in tabla.columns:

                        valor = fila[
                            columna.name
                        ]

                        registro[
                            columna.name
                        ] = convertir_valor(
                            valor,
                            columna
                        )

                    # SQLAlchemy gestiona IDENTITY_INSERT
                    # para columnas IDENTITY explícitas
                    # en el dialecto de SQL Server.

                    conexion.execute(
                        tabla.insert().values(
                            **registro
                        )
                    )

                    contador += 1

                print(
                    f"  Copiados {nombre}: "
                    f"{contador}"
                )

            # ------------------------------------------------
            # VERIFICAR CANTIDADES ANTES DE CONFIRMAR
            # ------------------------------------------------

            print(
                "\nVerificando cantidades..."
            )

            for nombre in tablas_modelo:

                origen = contar_sqlite(
                    sqlite,
                    nombre
                )

                destino = conexion.scalar(
                    select(func.count()).select_from(
                        tablas_destino[nombre]
                    )
                )

                if origen != destino:

                    raise RuntimeError(
                        f"Diferencia en {nombre}: "
                        f"SQLite={origen}, "
                        f"SQL Server={destino}"
                    )

                print(
                    f"  {nombre}: "
                    f"{origen} = {destino} OK"
                )

        # ----------------------------------------------------
        # TRANSACCIÓN CONFIRMADA
        # ----------------------------------------------------

        print("\n" + "=" * 65)

        print(
            "MIGRACIÓN COMPLETADA CORRECTAMENTE"
        )

        print(
            "Todos los registros fueron copiados "
            "y las cantidades coinciden."
        )

        print("=" * 65)

    finally:

        sqlite.close()


# ============================================================
# 8. EJECUTAR
# ============================================================

if __name__ == "__main__":
    migrar()
