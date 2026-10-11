# 💉 Sistema de Vacunación Infantil

Sistema web para la **gestión y consulta de registros de vacunación infantil**, desarrollado con **FastAPI**, **React** y **Microsoft SQL Server**.

> **Estado del proyecto:** en desarrollo. El frontend de autenticación y el dashboard están en construcción. Las reglas de calendario y equivalencias de vacunas deben validarse antes de utilizarlas para decisiones clínicas.

## 📋 Descripción

El sistema busca centralizar la información relacionada con pacientes, vacunas y aplicaciones registradas, con acceso diferenciado según el rol del usuario.

### Funcionalidades del backend

- Autenticación mediante correo electrónico y contraseña, con tokens JWT.
- Roles de usuario: **administrador**, **operador** y **visualizador**.
- Consulta y gestión de pacientes según los permisos del usuario.
- Registro y consulta de vacunas y aplicaciones.
- Historial y endpoints de consulta y estadísticas.
- Documentación interactiva de la API con Swagger.

> **Importante:** disponer de registros de vacunas no equivale a determinar cobertura, esquema completo ni dosis vencidas. Para esos cálculos se requieren fechas confiables, reglas clínicas validadas y equivalencias verificadas.

## 🛠️ Tecnologías

| Capa | Tecnología |
| --- | --- |
| Frontend | React, Vite, JavaScript, CSS |
| Navegación | React Router |
| Peticiones HTTP | Axios |
| Iconos | Lucide React |
| Backend | Python, FastAPI, Uvicorn |
| Acceso a datos | SQLAlchemy, pyodbc |
| Base de datos | Microsoft SQL Server Express |
| Autenticación | JWT |
| Control de versiones | Git y GitHub |

## 📁 Estructura general

```text
sistema_vacunacion/
├── backend/
│   ├── main.py                 # Aplicación FastAPI
│   ├── database.py             # Configuración de la base de datos
│   ├── routes/                 # Endpoints de la API
│   ├── services/               # Lógica de negocio y autenticación
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── context/            # Estado de autenticación
│   │   ├── pages/              # Pantallas de React
│   │   ├── services/           # Conexión con FastAPI
│   │   ├── styles/             # Archivos CSS
│   │   └── App.jsx             # Rutas principales
│   ├── package.json
│   └── ...
├── scripts/                    # Utilidades del proyecto, si están presentes
├── .gitignore
└── README.md
```

La estructura puede variar ligeramente conforme avance el desarrollo.

## ✅ Requisitos previos

Instalar en Windows:

1. **Python** (versión compatible con las dependencias del proyecto).
2. **Node.js y npm** (para React y Vite).
3. **Git**.
4. **Visual Studio Code** (recomendado).
5. **SQL Server Express** y, opcionalmente, **SQL Server Management Studio (SSMS)**.
6. **Microsoft ODBC Driver 18 for SQL Server**.

Comprobar la instalación desde PowerShell:

```powershell
python --version
node --version
npm --version
git --version
```

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```powershell
git clone https://github.com/TU_USUARIO/sistema-vacunacion-infantil.git
cd sistema-vacunacion-infantil
```

Sustituir `TU_USUARIO` por el usuario propietario del repositorio. Si el proyecto ya está descargado, basta con abrir su carpeta en Visual Studio Code.

### 2. Preparar el backend (FastAPI)

Desde la raíz del proyecto:

```powershell
# Crear un entorno virtual para aislar las dependencias.
python -m venv venv

# Activar el entorno virtual en PowerShell.
.\venv\Scripts\Activate.ps1
```

Si el repositorio incluye un archivo `requirements.txt` con las dependencias verificadas del backend, instalarlas mediante:

```powershell
python -m pip install -r requirements.txt
```

> Si `requirements.txt` aún no existe, debe generarse y revisarse desde el entorno de desarrollo que funciona antes de publicar una guía de instalación reproducible. No se recomienda instalar paquetes al azar ni asumir versiones.

### 3. Preparar SQL Server

1. Instalar e iniciar **SQL Server Express**.
2. Instalar **ODBC Driver 18 for SQL Server**.
3. Verificar el nombre de la instancia (en el entorno de desarrollo se utiliza `SQLEXPRESS`).
4. Crear o restaurar una base de datos **sin datos personales reales** para pruebas. El nombre utilizado durante el desarrollo es `VacunacionInfantil`.
5. Configurar `backend/database.py` con la instancia, el nombre de la base de datos y el método de autenticación correspondiente.
6. Ejecutar los scripts o migraciones del proyecto **solo si están incluidos y documentados**. No se incluye en este README un comando de inicialización no verificado.

**Nota:** en el entorno de desarrollo se utiliza autenticación de Windows para SQL Server. La configuración puede cambiar en otros equipos. Nunca publiques contraseñas o cadenas de conexión con credenciales reales.

### 4. Configurar la clave JWT

El backend necesita la variable de entorno `JWT_SECRET_KEY` para firmar los tokens de autenticación.

En **PowerShell**, desde la misma terminal donde ejecutarás FastAPI:

```powershell
# Generar una clave criptográficamente aleatoria.
$bytes = New-Object byte[] 64
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)

# Establecer la variable para esta sesión de PowerShell.
$env:JWT_SECRET_KEY = [Convert]::ToBase64String($bytes)
```

> La variable configurada así es temporal: al cerrar esa terminal será necesario volver a establecerla. En un despliegue real, utilizar un gestor de secretos o un mecanismo seguro de configuración. **No guardar ni subir la clave a GitHub.**

### 5. Iniciar el backend

Desde la carpeta raíz, con el entorno virtual activo y la variable JWT configurada:

```powershell
python -m uvicorn backend.main:app --reload
```

Direcciones locales:

- API: <http://127.0.0.1:8000>
- Documentación Swagger: <http://127.0.0.1:8000/docs>

> Si la ruta raíz `/` no está implementada, puede no mostrar una página; utiliza `/docs` para consultar la API.

### 6. Preparar el frontend (React)

Abrir **otra terminal** de Visual Studio Code, dejando FastAPI en ejecución:

```powershell
cd frontend

# Instalar las dependencias definidas en package.json.
npm install

# Iniciar el servidor de desarrollo de Vite.
npm run dev
```

Abrir: <http://localhost:5173/>

El frontend realiza peticiones a FastAPI en `http://127.0.0.1:8000`. Para el desarrollo local, el backend debe permitir mediante CORS el origen `http://localhost:5173` (y, si se utiliza, `http://127.0.0.1:5173`).

## 🔐 Autenticación

El backend dispone de los siguientes endpoints:

| Método | Endpoint | Función |
| --- | --- | --- |
| `POST` | `/auth/login` | Iniciar sesión y obtener un token JWT |
| `GET` | `/auth/me` | Consultar el usuario autenticado |

El login utiliza un formulario `application/x-www-form-urlencoded` con los campos `username` (**correo electrónico**) y `password`.

Para endpoints protegidos, enviar la cabecera:

```http
Authorization: Bearer TOKEN_JWT
```

Los roles previstos son:

- **Administrador:** gestión completa, según los permisos configurados en el backend.
- **Operador:** funciones operativas permitidas.
- **Visualizador:** acceso de consulta.

Los permisos **deben validarse en el backend**, no solamente ocultando botones en React.

## 🧪 Pruebas básicas

1. Iniciar SQL Server y comprobar la conexión desde el backend.
2. Ejecutar FastAPI y abrir `/docs`.
3. Probar `POST /auth/login` con una cuenta de prueba autorizada.
4. Probar `GET /auth/me` con el token recibido.
5. Ejecutar React y abrir `http://localhost:5173/`.
6. Verificar el inicio y cierre de sesión desde el navegador.

**No utilizar información identificable de pacientes en capturas, incidencias o ejemplos publicados.**

## 🛡️ Seguridad y privacidad

Este proyecto trata datos potencialmente sensibles de salud. Antes de subir cambios al repositorio:

- No incluir bases de datos reales, exportaciones, respaldos ni registros identificables de pacientes.
- No incluir archivos `.env`, claves JWT, contraseñas, tokens ni credenciales de SQL Server.
- Revisar los archivos preparados con `git diff --cached --name-only` antes de hacer un commit.
- Mantener el repositorio **privado** mientras se desarrolla y revisa la seguridad.
- Utilizar datos sintéticos o anonimizados para pruebas y demostraciones.
- Evitar guardar tokens en almacenamiento persistente del navegador sin una evaluación de seguridad.
- Validar las reglas del calendario de vacunación con fuentes oficiales y profesionales competentes antes de usarlas en decisiones clínicas.

> Si una credencial o datos sensibles ya fueron incluidos en un commit, añadirlos después a `.gitignore` **no los elimina del historial de Git**. Se requiere retirar la información del historial y rotar las credenciales expuestas.

## 🔄 Guardar futuros cambios en GitHub

Desde la raíz del proyecto:

```powershell
# Revisar qué archivos cambiaron.
git status

# Preparar cambios.
git add .

# Revisar los nombres de los archivos preparados.
git diff --cached --name-only

# Guardar una versión.
git commit -m "Describir los cambios realizados"

# Enviar al repositorio remoto.
git push
```

## 🗺️ Próximas mejoras

- [ ] Dashboard de React con estadísticas y navegación por roles.
- [ ] Pantallas de pacientes, vacunas y aplicaciones.
- [ ] Gestión visual de usuarios y permisos.
- [ ] Validación del esquema de vacunación y equivalencias.
- [ ] Pruebas automatizadas y documentación de despliegue.
- [ ] Guía reproducible de inicialización de una base de datos de demostración.

## 📌 Nota final

Proyecto en desarrollo con fines de aprendizaje y construcción de una herramienta de gestión. **No constituye una herramienta de diagnóstico ni de recomendación clínica validada.**
