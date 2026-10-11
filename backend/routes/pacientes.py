
# ============================================================
# SISTEMA DE SEGUIMIENTO DE VACUNACIÓN INFANTIL
# ARCHIVO: backend/routes/pacientes.py
#
# FUNCIÓN:
# Administrar la información de los pacientes.
#
# OPERACIONES:
# 1. Crear pacientes.
# 2. Listar pacientes.
# 3. Buscar pacientes por nombre.
# 4. Consultar un paciente por ID.
# 5. Actualizar información del paciente.
# 6. Consultar su estado de vacunación.
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

# unicodedata:
# Permite normalizar textos y eliminar acentos.

import unicodedata

# date:
# Permite trabajar con fechas de nacimiento.

from datetime import date

# Optional:
# Permite definir campos opcionales.

from typing import Optional

# FastAPI:
# APIRouter: agrupa los endpoints.
# Depends: obtiene dependencias como la base de datos.
# HTTPException: devuelve errores HTTP.

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

# Pydantic:
# Valida los datos recibidos desde la API.

from pydantic import (
    BaseModel,
    Field
)

# SQLAlchemy:
# Permite realizar consultas a SQLite.

from sqlalchemy.orm import Session

# Conexión a la base de datos.

from backend.database import get_db

# Modelo de pacientes.

from backend.models.paciente import Paciente

# Servicio encargado de calcular el estado
# de vacunación de cada paciente.

from backend.services.estado_vacunacion_service import (
    calcular_estado_vacunacion
)


# ============================================================
# 2. CONFIGURAR RUTAS
# ============================================================

# Todas las rutas de este archivo comenzarán con:
#
# /pacientes
#
# Ejemplo:
# GET /pacientes/

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)


# ============================================================
# 3. NORMALIZAR TEXTOS
# ============================================================

def normalizar_texto(texto: str) -> str:
    """
    Convierte un texto a mayúsculas, elimina
    espacios innecesarios y elimina acentos.

    Ejemplo:

    Entrada:
        José Ramón Pérez

    Resultado:
        JOSE RAMON PEREZ

    Esto facilita las búsquedas en la base de datos.
    """

    # Eliminar espacios al inicio y al final.
    # Convertir el texto a mayúsculas.

    texto = texto.strip().upper()

    # Eliminar espacios repetidos.

    texto = " ".join(
        texto.split()
    )

    # Eliminar acentos.

    texto = "".join(
        caracter
        for caracter in unicodedata.normalize(
            "NFD",
            texto
        )
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


# ============================================================
# 4. MODELO PARA CREAR PACIENTES
# ============================================================

# Define qué información acepta la API
# cuando registramos un paciente nuevo.
#
# Ejemplo:
# POST /pacientes/

class PacienteCrear(BaseModel):

    # Nombre obligatorio.
    nombres: str = Field(
        min_length=2,
        max_length=100
    )

    # Apellido obligatorio.
    apellidos: str = Field(
        min_length=2,
        max_length=100
    )

    # Fecha de nacimiento opcional.
    fecha_nacimiento: Optional[date] = None

    # Procedencia de la fecha.
    origen_fecha_nacimiento: Optional[str] = None

    # Edad informada por SISVACU.
    edad_reportada_anios: Optional[int] = Field(
        default=None,
        ge=0,
        le=6
    )

    # Sexo del paciente.
    sexo: Optional[str] = None

    # Información de nacimiento.
    nacimiento_prematuro: Optional[bool] = None

    semanas_gestacion: Optional[int] = Field(
        default=None,
        ge=22,
        le=42
    )

    peso_nacimiento_gr: Optional[int] = Field(
        default=None,
        ge=400,
        le=6000
    )

    # Observaciones adicionales.
    observaciones: Optional[str] = None


# ============================================================
# 5. MODELO PARA ACTUALIZAR PACIENTES
# ============================================================

# Todos los campos son opcionales porque
# podemos actualizar solamente uno o varios.
#
# Ejemplo:
# Cambiar la fecha de nacimiento sin modificar
# el nombre ni los demás datos.

class PacienteActualizar(BaseModel):

    nombres: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    apellidos: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    fecha_nacimiento: Optional[date] = None

    origen_fecha_nacimiento: Optional[str] = None

    edad_reportada_anios: Optional[int] = Field(
        default=None,
        ge=0,
        le=6
    )

    sexo: Optional[str] = None

    nacimiento_prematuro: Optional[bool] = None

    semanas_gestacion: Optional[int] = Field(
        default=None,
        ge=22,
        le=42
    )

    peso_nacimiento_gr: Optional[int] = Field(
        default=None,
        ge=400,
        le=6000
    )

    estado: Optional[str] = None

    completitud: Optional[str] = None

    observaciones: Optional[str] = None


# ============================================================
# 6. CREAR PACIENTE
# ============================================================

# ENDPOINT:
# POST /pacientes/
#
# Recibe los datos de un paciente y los guarda
# en la base de datos.

@router.post("/")
def crear_paciente(
    datos: PacienteCrear,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # VALIDAR FECHA DE NACIMIENTO
    # --------------------------------------------------------

    # Un paciente no puede tener una fecha
    # de nacimiento posterior a hoy.

    if (
        datos.fecha_nacimiento is not None
        and datos.fecha_nacimiento > date.today()
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "La fecha de nacimiento "
                "no puede ser futura"
            )
        )

    # --------------------------------------------------------
    # NORMALIZAR NOMBRE Y APELLIDO
    # --------------------------------------------------------

    nombres = normalizar_texto(
        datos.nombres
    )

    apellidos = normalizar_texto(
        datos.apellidos
    )

    # Generamos el campo utilizado para búsquedas.

    nombre_busqueda = normalizar_texto(
        f"{nombres} {apellidos}"
    )

    # --------------------------------------------------------
    # CREAR OBJETO PACIENTE
    # --------------------------------------------------------

    paciente = Paciente(
        nombres=nombres,
        apellidos=apellidos,
        nombre_busqueda=nombre_busqueda,

        fecha_nacimiento=datos.fecha_nacimiento,

        origen_fecha_nacimiento=(
            datos.origen_fecha_nacimiento
        ),

        edad_reportada_anios=(
            datos.edad_reportada_anios
        ),

        sexo=datos.sexo,

        nacimiento_prematuro=(
            1 if datos.nacimiento_prematuro is True
            else 0 if datos.nacimiento_prematuro is False
            else None
        ),

        semanas_gestacion=datos.semanas_gestacion,

        peso_nacimiento_gr=datos.peso_nacimiento_gr,

        estado="activo",

        completitud="minimo",

        observaciones=datos.observaciones
    )

    # --------------------------------------------------------
    # GUARDAR EN SQLITE
    # --------------------------------------------------------

    # Agregar el paciente a la sesión.

    db.add(paciente)

    # Confirmar los cambios.

    db.commit()

    # Actualizar el objeto con los datos guardados.

    db.refresh(paciente)

    # Devolver el paciente registrado.

    return paciente


# ============================================================
# 7. LISTAR PACIENTES
# ============================================================

# ENDPOINT:
# GET /pacientes/
#
# Devuelve todos los pacientes registrados.

@router.get("/")
def listar_pacientes(
    db: Session = Depends(get_db)
):

    # Consultar pacientes y ordenarlos
    # por apellido y nombre.

    pacientes = (
        db.query(Paciente)
        .order_by(
            Paciente.apellidos,
            Paciente.nombres
        )
        .all()
    )

    return pacientes


# ============================================================
# 8. BUSCAR PACIENTES POR NOMBRE
# ============================================================

# ENDPOINT:
# GET /pacientes/buscar?nombre=JUAN
#
# Permite buscar coincidencias parciales.
#
# Ejemplo:
# Buscar "JUAN" puede devolver:
#
# JUAN PEREZ
# JUAN CARLOS GOMEZ

@router.get("/buscar")
def buscar_pacientes(
    nombre: str,
    db: Session = Depends(get_db)
):

    # Normalizar el texto ingresado.

    nombre_normalizado = normalizar_texto(
        nombre
    )

    # Buscar coincidencias.

    pacientes = (
        db.query(Paciente)
        .filter(
            Paciente.nombre_busqueda.contains(
                nombre_normalizado
            )
        )
        .all()
    )

    return pacientes


# ============================================================
# 9. CONSULTAR PACIENTE POR ID
# ============================================================

# ENDPOINT:
# GET /pacientes/1

@router.get("/{paciente_id}")
def obtener_paciente(
    paciente_id: int,
    db: Session = Depends(get_db)
):

    # Buscar el paciente.

    paciente = db.get(
        Paciente,
        paciente_id
    )

    # Comprobar que existe.

    if paciente is None:

        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado"
        )

    return paciente


# ============================================================
# 10. ACTUALIZAR PACIENTE
# ============================================================

# ENDPOINT:
# PUT /pacientes/1
#
# Permite completar o corregir información
# de un paciente existente.

@router.put("/{paciente_id}")
def actualizar_paciente(
    paciente_id: int,
    datos: PacienteActualizar,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # BUSCAR PACIENTE
    # --------------------------------------------------------

    paciente = db.get(
        Paciente,
        paciente_id
    )

    if paciente is None:

        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado"
        )

    # --------------------------------------------------------
    # OBTENER CAMPOS ENVIADOS
    # --------------------------------------------------------

    # exclude_unset=True permite actualizar
    # solamente los campos que el usuario envió.

    cambios = datos.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # VALIDAR FECHA
    # --------------------------------------------------------

    fecha = cambios.get(
        "fecha_nacimiento"
    )

    if (
        fecha is not None
        and fecha > date.today()
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "La fecha de nacimiento "
                "no puede ser futura"
            )
        )

    # --------------------------------------------------------
    # CONVERTIR NACIMIENTO PREMATURO
    # --------------------------------------------------------

    if "nacimiento_prematuro" in cambios:

        valor = cambios[
            "nacimiento_prematuro"
        ]

        if valor is True:

            cambios[
                "nacimiento_prematuro"
            ] = 1

        elif valor is False:

            cambios[
                "nacimiento_prematuro"
            ] = 0

        else:

            cambios[
                "nacimiento_prematuro"
            ] = None

    # --------------------------------------------------------
    # APLICAR CAMBIOS
    # --------------------------------------------------------

    for campo, valor in cambios.items():

        # Normalizar nombres y apellidos.

        if (
            campo in ["nombres", "apellidos"]
            and valor is not None
        ):

            valor = normalizar_texto(
                valor
            )

        # Modificar el campo correspondiente.

        setattr(
            paciente,
            campo,
            valor
        )

    # --------------------------------------------------------
    # ACTUALIZAR NOMBRE DE BÚSQUEDA
    # --------------------------------------------------------

    paciente.nombre_busqueda = normalizar_texto(
        f"{paciente.nombres} {paciente.apellidos}"
    )

    # --------------------------------------------------------
    # GUARDAR CAMBIOS
    # --------------------------------------------------------

    db.commit()

    db.refresh(paciente)

    return paciente


# ============================================================
# 11. CONSULTAR ESTADO DE VACUNACIÓN
# ============================================================

# ENDPOINT:
# GET /pacientes/1/estado-vacunacion
#
# Obtiene las aplicaciones registradas y compara
# las dosis con las reglas activas del esquema.
#
# IMPORTANTE:
# Las reglas del calendario 2026 siguen inactivas
# hasta verificar las equivalencias con SISVACU.
#
# Por eso todavía no se deben interpretar
# los resultados como una evaluación clínica definitiva.

@router.get("/{paciente_id}/estado-vacunacion")
def estado_vacunacion_paciente(
    paciente_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # BUSCAR PACIENTE
    # --------------------------------------------------------

    paciente = db.get(
        Paciente,
        paciente_id
    )

    # --------------------------------------------------------
    # VALIDAR EXISTENCIA
    # --------------------------------------------------------

    if paciente is None:

        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado"
        )

    # --------------------------------------------------------
    # CALCULAR ESTADO
    # --------------------------------------------------------

    # El servicio realiza la comparación
    # y devuelve los resultados.

    resultado = calcular_estado_vacunacion(
        paciente,
        db
    )

    return resultado
