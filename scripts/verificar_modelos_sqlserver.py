
# ============================================================
# SISTEMA DE VACUNACIÓN INFANTIL
# ARCHIVO: scripts/verificar_modelos_sqlserver.py
#
# OBJETIVO:
# Verificar que SQLAlchemy pueda preparar las instrucciones
# CREATE TABLE para Microsoft SQL Server.
#
# SEGURIDAD:
# Este script NO crea, modifica ni elimina tablas.
# Tampoco modifica los datos de SQLite.
# ============================================================

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mssql

from backend.database import Base

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
# 2. REVISAR LAS TABLAS
# ============================================================

def verificar_modelos():

    print("=" * 65)
    print("VERIFICACIÓN DE MODELOS PARA SQL SERVER")
    print("=" * 65)

    dialecto = mssql.dialect()

    errores = []

    tablas = list(
        Base.metadata.sorted_tables
    )

    print(
        f"\nTablas encontradas: {len(tablas)}"
    )

    # --------------------------------------------------------
    # COMPILAR CREATE TABLE PARA CADA MODELO
    # --------------------------------------------------------

    for tabla in tablas:

        print(
            f"\nVerificando tabla: {tabla.name}"
        )

        try:

            instruccion = CreateTable(
                tabla
            ).compile(
                dialect=dialecto
            )

            print("RESULTADO: CORRECTO")

            print(
                f"Columnas: {len(tabla.columns)}"
            )

            print(
                f"Claves foráneas: "
                f"{len(tabla.foreign_keys)}"
            )

        except Exception as error:

            print("RESULTADO: ERROR")

            print(error)

            errores.append(
                (tabla.name, str(error))
            )

    # --------------------------------------------------------
    # MOSTRAR RESULTADO GENERAL
    # --------------------------------------------------------

    print("\n" + "=" * 65)

    if errores:

        print(
            "SE ENCONTRARON PROBLEMAS"
        )

        for nombre, mensaje in errores:

            print(
                f"\nTabla: {nombre}"
            )

            print(
                f"Problema: {mensaje}"
            )

    else:

        print(
            "TODOS LOS CREATE TABLE "
            "SE COMPILARON CORRECTAMENTE"
        )

        print(
            "La estructura está lista "
            "para continuar con las pruebas."
        )

    print("=" * 65)

    return len(errores) == 0


# ============================================================
# 3. EJECUTAR
# ============================================================

if __name__ == "__main__":

    correcto = verificar_modelos()

    if not correcto:

        raise SystemExit(1)
