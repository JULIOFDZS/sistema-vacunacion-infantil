/*
====================================================
 ARCHIVO: src/context/AuthContext.jsx
 FUNCIÓN: Administrar la autenticación del sistema
====================================================
*/

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import api, {
  configurarToken,
  registrarExpiracionSesion,
} from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // null significa que todavía no inició sesión.
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(false);

  /*
  FUNCIÓN: iniciarSesion
  Envía el correo y la contraseña a /auth/login
  y luego consulta el perfil con /auth/me.
  */
  const iniciarSesion = async (email, password) => {
    setCargando(true);

    try {
      const datos = new URLSearchParams();
      datos.append("username", email);
      datos.append("password", password);

      const respuesta = await api.post("/auth/login", datos, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const token = respuesta.data.access_token;

      if (!token) {
        throw new Error("No se recibió un token.");
      }

      configurarToken(token);

      try {
        const perfil = await api.get("/auth/me");
        setUsuario(perfil.data);
      } catch (error) {
        configurarToken(null);
        throw error;
      }

      return true;
    } finally {
      setCargando(false);
    }
  };

  const cerrarSesion = useCallback(() => {
    configurarToken(null);
    setUsuario(null);
  }, []);

  // Si el backend responde 401, cerramos la sesión.
  useEffect(() => {
    registrarExpiracionSesion(cerrarSesion);
    return () => registrarExpiracionSesion(null);
  }, [cerrarSesion]);

  // Permisos según el rol. El backend es quien realmente
  // los valida; esto solo adapta la interfaz.
  const rol = usuario?.rol;
  const esAdmin = rol === "admin";
  const puedeEscribir = rol === "admin" || rol === "operador";

  return (
    <AuthContext.Provider
      value={{
        usuario,
        cargando,
        iniciarSesion,
        cerrarSesion,
        esAdmin,
        puedeEscribir,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const contexto = useContext(AuthContext);

  if (!contexto) {
    throw new Error("useAuth debe utilizarse dentro de AuthProvider");
  }

  return contexto;
}
