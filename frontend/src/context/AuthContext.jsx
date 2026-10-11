
/*
====================================================
 ARCHIVO: src/context/AuthContext.jsx
 FUNCIÓN: Administrar la autenticación del sistema
====================================================
*/

// Importamos herramientas de React.
import {
  createContext,
  useContext,
  useState,
} from "react";

// Importamos nuestra conexión con FastAPI.
import api, { configurarToken } from "../services/api";

// Creamos un contexto para compartir los datos del usuario.
const AuthContext = createContext(null);

/*
COMPONENTE: AuthProvider

Permite que cualquier componente del sistema
pueda acceder a la información del usuario.
*/
export function AuthProvider({ children }) {

  // Guarda los datos del usuario autenticado.
  // null significa que todavía no inició sesión.
  const [usuario, setUsuario] = useState(null);

  // Indica si estamos verificando las credenciales.
  const [cargando, setCargando] = useState(false);

  /*
  FUNCIÓN: iniciarSesion

  Recibe el correo electrónico y la contraseña.
  Envía esos datos al endpoint /auth/login de FastAPI.
  */
  const iniciarSesion = async (email, password) => {

    // Activamos el estado de carga.
    setCargando(true);

    try {

      // FastAPI espera los datos como formulario.
      const datos = new URLSearchParams();

      // En OAuth2, "username" contiene el correo.
      datos.append("username", email);

      // Agregamos la contraseña.
      datos.append("password", password);

      // Enviamos la solicitud de inicio de sesión.
      const respuesta = await api.post(
        "/auth/login",
        datos,
        {
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
        }
      );

      // Obtenemos el token que devuelve FastAPI.
      const token = respuesta.data.access_token;

      // Comprobamos que el servidor devolvió un token.
      if (!token) {
        throw new Error("No se recibió un token.");
      }

      // Configuramos el token para las próximas peticiones.
      configurarToken(token);

      try {

        // Consultamos los datos reales del usuario.
        const perfil = await api.get("/auth/me");

        // Guardamos el usuario en el estado de React.
        setUsuario(perfil.data);

      } catch (error) {

        // Si falla la consulta del perfil,
        // eliminamos el token por seguridad.
        configurarToken(null);

        // Propagamos el error al formulario.
        throw error;
      }

      // Indicamos que el inicio de sesión fue exitoso.
      return true;

    } finally {

      // Finalizamos el estado de carga,
      // tanto si hubo éxito como si ocurrió un error.
      setCargando(false);

    }
  };

  /*
  FUNCIÓN: cerrarSesion

  Elimina el token y los datos del usuario.
  */
  const cerrarSesion = () => {

    configurarToken(null);

    setUsuario(null);

  };

  // Compartimos las funciones y variables.
  return (
    <AuthContext.Provider
      value={{
        usuario,
        cargando,
        iniciarSesion,
        cerrarSesion,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/*
HOOK: useAuth

Permite acceder fácilmente al contexto
desde Login, Dashboard y otros componentes.
*/
export function useAuth() {

  const contexto = useContext(AuthContext);

  // Evitamos utilizar el contexto fuera del proveedor.
  if (!contexto) {
    throw new Error(
      "useAuth debe utilizarse dentro de AuthProvider"
    );
  }

  return contexto;
}
