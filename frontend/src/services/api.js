
/*
====================================================
 ARCHIVO: src/services/api.js
 FUNCIÓN: Configurar la conexión con FastAPI
====================================================
*/

// Importamos Axios, una librería para hacer peticiones HTTP.
import axios from "axios";

// Creamos una conexión reutilizable con nuestro backend.
const api = axios.create({

  // Dirección donde se está ejecutando FastAPI.
  baseURL: "http://127.0.0.1:8000",

  // Tiempo máximo de espera: 10 segundos.
  timeout: 10000,

});

/*
FUNCIÓN: configurarToken

Sirve para agregar el token de autenticación a las
peticiones que realizamos al backend.

FastAPI utiliza ese token para identificar al usuario.
*/
export function configurarToken(token) {

  // Si recibimos un token válido...
  if (token) {

    // Lo agregamos a la cabecera Authorization.
    api.defaults.headers.common.Authorization =
      `Bearer ${token}`;

  } else {

    // Si no hay token, eliminamos la autorización.
    // Esto se utiliza al cerrar sesión.
    delete api.defaults.headers.common.Authorization;

  }
}

// Exportamos la conexión para utilizarla en otros archivos.
export default api;
