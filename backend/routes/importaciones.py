
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/importaciones.py
#
# FUNCIÓN:
# Administrar la importación de archivos Excel SISVACU.
#
# ENDPOINTS:
# POST /importaciones/sisvacu/vista-previa
# POST /importaciones/sisvacu/confirmar
#
# IMPORTANTE:
# La vista previa no modifica la base de datos.
# La confirmación sí guarda información.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

# Conexión con SQLite.

from backend.database import get_db

# Servicio de lectura y validación SISVACU.

from backend.services.sisvacu_service import (
    leer_sisvacu,
    normalizar_texto
)

# Modelos de base de datos.

from backend.models.paciente import Paciente

from backend.models.identificador import (
    IdentificadorPaciente
)

from backend.models.vacuna import Vacuna

from backend.models.aplicacion import Aplicacion


# ============================================================
# 2. CONFIGURAR ROUTER
# ============================================================

router = APIRouter(
    prefix="/importaciones",
    tags=["Importaciones SISVACU"]
)


# ============================================================
# 3. VALIDAR ARCHIVO EXCEL
# ============================================================

def validar_archivo_excel(archivo: UploadFile):
    """
    Comprueba que el archivo tenga nombre
    y extensión .xlsx.

    La lectura posterior verificará si realmente
    contiene un Excel válido.
    """

    if not archivo.filename:

        raise HTTPException(
            status_code=400,
            detail="El archivo no tiene nombre."
        )

    if not archivo.filename.lower().endswith(".xlsx"):

        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos .xlsx"
        )


# ============================================================
# 4. VISTA PREVIA DEL SISVACU
# ============================================================

@router.post("/sisvacu/vista-previa")
async def vista_previa_sisvacu(
    archivo: UploadFile = File(...)
):
    """
    Permite revisar el Excel antes de importarlo.

    Devuelve:
    - Cantidad de pacientes.
    - Filas correctas.
    - Advertencias.
    - Errores.
    - Vacunas registradas.

    No guarda nada en SQLite.
    """

    # --------------------------------------------------------
    # VALIDAR EXTENSIÓN
    # --------------------------------------------------------

    validar_archivo_excel(
        archivo
    )

    # --------------------------------------------------------
    # LEER CONTENIDO
    # --------------------------------------------------------

    contenido = await archivo.read()

    if not contenido:

        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío."
        )

    # --------------------------------------------------------
    # ANALIZAR EXCEL
    # --------------------------------------------------------

    resultado = leer_sisvacu(
        contenido
    )

    # --------------------------------------------------------
    # DEVOLVER RESULTADO
    # --------------------------------------------------------

    return {
        "archivo": archivo.filename,
        **resultado
    }


# ============================================================
# 5. CONFIRMAR IMPORTACIÓN SISVACU
# ============================================================

@router.post("/sisvacu/confirmar")
async def confirmar_importacion_sisvacu(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Guarda los datos validados en SQLite.

    Si el paciente ya existe según su identificador,
    reutiliza su registro.

    Si el paciente es nuevo, lo crea.

    Evita registrar dos veces la misma dosis
    para el mismo paciente.
    """

    # --------------------------------------------------------
    # VALIDAR ARCHIVO
    # --------------------------------------------------------

    validar_archivo_excel(
        archivo
    )

    contenido = await archivo.read()

    if not contenido:

        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío."
        )

    # --------------------------------------------------------
    # LEER Y VALIDAR SISVACU
    # --------------------------------------------------------

    resultado = leer_sisvacu(
        contenido
    )

    # --------------------------------------------------------
    # VALIDAR FORMATO GENERAL
    # --------------------------------------------------------

    if not resultado["valido"]:

        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": (
                    "El archivo no tiene el formato esperado."
                ),
                "errores": resultado["errores"]
            }
        )

    # --------------------------------------------------------
    # DETENER IMPORTACIÓN SI HAY ERRORES
    # --------------------------------------------------------

    if resultado["filas_error"] > 0:

        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": (
                    "La importación contiene filas con "
                    "errores. Revise primero la vista previa."
                ),
                "filas_error": resultado["filas_error"]
            }
        )

    # --------------------------------------------------------
    # EVITAR DUPLICADOS DE PACIENTES SIN DOCUMENTO
    # --------------------------------------------------------

    # Sin un identificador estable no podemos garantizar
    # que una segunda importación encuentre al mismo niño.
    #
    # Por seguridad, estas filas requieren un mecanismo
    # de vinculación o revisión manual antes de confirmar.

    filas_sin_documento = [
        fila["fila"]
        for fila in resultado["filas"]
        if fila["tipo_documento"] == "sin_documento"
    ]

    if filas_sin_documento:

        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": (
                    "Existen pacientes sin identificador. "
                    "La confirmación se detuvo para evitar "
                    "duplicados en futuras importaciones."
                ),
                "filas": filas_sin_documento
            }
        )

    # --------------------------------------------------------
    # CONTADORES DE IMPORTACIÓN
    # --------------------------------------------------------

    pacientes_creados = 0
    pacientes_actualizados = 0

    identificadores_creados = 0

    vacunas_creadas = 0

    aplicaciones_creadas = 0
    aplicaciones_existentes = 0

    # --------------------------------------------------------
    # DICCIONARIO DE VACUNAS
    # --------------------------------------------------------

    # Permite consultar rápidamente una vacuna
    # utilizando su código SISVACU.

    vacunas_por_codigo = {}

    # --------------------------------------------------------
    # INICIAR TRANSACCIÓN
    # --------------------------------------------------------

    # Todos los cambios se confirman juntos.
    # Si ocurre un error, se deshacen con rollback().

    try:

        # ====================================================
        # 6. REGISTRAR VACUNAS DEL EXCEL
        # ====================================================

        for codigo in resultado["columnas_vacunas"]:

            # Buscar vacuna existente.

            vacuna = (
                db.query(Vacuna)
                .filter(
                    Vacuna.codigo == codigo
                )
                .first()
            )

            # Si no existe, crearla.

            if vacuna is None:

                vacuna = Vacuna(
                    codigo=codigo,
                    nombre=codigo,
                    activa=True
                )

                db.add(vacuna)

                # flush permite obtener el ID
                # sin confirmar todavía la transacción.

                db.flush()

                vacunas_creadas += 1

            # Guardar referencia en el diccionario.

            vacunas_por_codigo[codigo] = vacuna

        # ====================================================
        # 7. RECORRER PACIENTES DEL EXCEL
        # ====================================================

        for fila in resultado["filas"]:

            documento = fila["documento"]

            tipo_documento = fila["tipo_documento"]

            paciente = None

            # ------------------------------------------------
            # BUSCAR PACIENTE POR IDENTIFICADOR
            # ------------------------------------------------

            identificador = (
                db.query(IdentificadorPaciente)
                .filter(
                    IdentificadorPaciente.tipo
                    == tipo_documento,

                    IdentificadorPaciente.numero
                    == documento
                )
                .first()
            )

            # Si encontramos el identificador,
            # utilizamos el paciente relacionado.

            if identificador:

                paciente = identificador.paciente

            # ------------------------------------------------
            # CREAR PACIENTE SI NO EXISTE
            # ------------------------------------------------

            if paciente is None:

                nombres = normalizar_texto(
                    fila["nombres"]
                )

                apellidos = normalizar_texto(
                    fila["apellidos"]
                )

                nombre_busqueda = normalizar_texto(
                    f"{nombres} {apellidos}"
                )

                paciente = Paciente(
                    nombres=nombres,
                    apellidos=apellidos,
                    nombre_busqueda=nombre_busqueda,
                    edad_reportada_anios=fila["edad"],
                    estado="activo",
                    completitud="minimo",
                    observaciones=(
                        "Importado desde SISVACU. "
                        f"Nombre original: {fila['persona']}"
                    )
                )

                db.add(paciente)

                db.flush()

                pacientes_creados += 1

                # --------------------------------------------
                # GUARDAR IDENTIFICADOR
                # --------------------------------------------

                nuevo_identificador = IdentificadorPaciente(
                    paciente_id=paciente.id,
                    tipo=tipo_documento,
                    numero=documento,
                    vigente=True,
                    origen="SISVACU"
                )

                db.add(nuevo_identificador)

                identificadores_creados += 1

            # ------------------------------------------------
            # ACTUALIZAR PACIENTE EXISTENTE
            # ------------------------------------------------

            else:

                # Actualizamos la edad reportada,
                # pero conservamos los demás datos.

                paciente.edad_reportada_anios = fila["edad"]

                pacientes_actualizados += 1

            # =================================================
            # 8. REGISTRAR DOSIS APLICADAS
            # =================================================

            for codigo in fila["dosis_aplicadas"]:

                vacuna = vacunas_por_codigo[codigo]

                # ---------------------------------------------
                # BUSCAR APLICACIÓN EXISTENTE
                # ---------------------------------------------

                aplicacion_existente = (
                    db.query(Aplicacion)
                    .filter(
                        Aplicacion.paciente_id
                        == paciente.id,

                        Aplicacion.vacuna_id
                        == vacuna.id
                    )
                    .first()
                )

                # Si la dosis ya existe, no duplicarla.

                if aplicacion_existente:

                    aplicaciones_existentes += 1
                    continue

                # ---------------------------------------------
                # CREAR APLICACIÓN
                # ---------------------------------------------

                nueva_aplicacion = Aplicacion(
                    paciente_id=paciente.id,
                    vacuna_id=vacuna.id,

                    # El Excel no contiene la fecha
                    # individual de aplicación.
                    fecha_aplicacion=None,
                    fecha_confirmada=False,

                    origen="SISVACU",
                    anulada=False
                )

                db.add(
                    nueva_aplicacion
                )

                aplicaciones_creadas += 1

        # ====================================================
        # 9. CONFIRMAR TRANSACCIÓN
        # ====================================================

        db.commit()

    except Exception as error:

        # ----------------------------------------------------
        # DESHACER CAMBIOS EN CASO DE ERROR
        # ----------------------------------------------------

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": (
                    "Ocurrió un error al guardar "
                    "la importación."
                ),
                "error": str(error)
            }
        )

    # ========================================================
    # 10. DEVOLVER RESULTADO
    # ========================================================

    return {
        "mensaje": (
            "Importación SISVACU realizada correctamente."
        ),
        "archivo": archivo.filename,
        "filas_procesadas": resultado["total_filas"],
        "pacientes_creados": pacientes_creados,
        "pacientes_actualizados": pacientes_actualizados,
        "identificadores_creados": identificadores_creados,
        "vacunas_creadas": vacunas_creadas,
        "aplicaciones_creadas": aplicaciones_creadas,
        "aplicaciones_ya_existentes": aplicaciones_existentes
    }
