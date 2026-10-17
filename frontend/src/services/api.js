/*
====================================================
 ARCHIVO: src/services/api.js
 FUNCIÓN: Configurar la conexión con FastAPI
====================================================
*/

import axios from "axios";

// La URL del backend puede cambiarse con VITE_API_URL
// (por ejemplo en un archivo .env.local). Por defecto
// se usa el FastAPI local del entorno de desarrollo.
const BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Función que App registra para cerrar la sesión cuando
// el backend responde 401 (token vencido o inválido).
let alExpirarSesion = null;

export function registrarExpiracionSesion(funcion) {
  alExpirarSesion = funcion;
}

api.interceptors.response.use(
  (respuesta) => respuesta,
  (error) => {
    const url = error.config?.url || "";
    const esLogin = url.includes("/auth/login");

    // Un 401 fuera del login significa sesión vencida.
    if (error.response?.status === 401 && !esLogin) {
      alExpirarSesion?.();
    }

    return Promise.reject(error);
  }
);

/*
FUNCIÓN: configurarToken

Agrega (o quita) el token JWT de las peticiones.
El token se guarda solo en memoria, tal como indica
el README del proyecto.
*/
export function configurarToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export default api;
