
/*
====================================================
 ARCHIVO: src/App.jsx
 FUNCIÓN: Administrar la navegación del sistema
====================================================
*/

// Importamos las herramientas de navegación.
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

// Importamos el sistema de autenticación.
import {
  AuthProvider,
  useAuth,
} from "./context/AuthContext";

// Importamos la pantalla de login.
import Login from "./pages/Login";

/*
COMPONENTE: DashboardTemporal

Es una pantalla provisional.
En el Bloque 13.3 crearemos el Dashboard completo.
*/
function DashboardTemporal() {

  // Obtenemos los datos del usuario y el cierre de sesión.
  const { usuario, cerrarSesion } = useAuth();

  return (
    <main style={{ padding: 40, fontFamily: "Arial" }}>

      <h1>¡Bienvenido a VacunaControl!</h1>

      <p>
        Inicio de sesión realizado correctamente.
      </p>

      {/* Mostramos los datos devueltos por /auth/me.
          Esto es únicamente para pruebas de desarrollo. */}
      <pre>
        {JSON.stringify(usuario, null, 2)}
      </pre>

      {/* Botón para cerrar sesión. */}
      <button onClick={cerrarSesion}>
        Cerrar sesión
      </button>

    </main>
  );
}

/*
COMPONENTE: RutaProtegida

Evita que una persona sin sesión iniciada
acceda al Dashboard.
*/
function RutaProtegida({ children }) {

  const { usuario } = useAuth();

  // Si no hay usuario, enviamos al login.
  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  // Si está autenticado, mostramos la pantalla.
  return children;
}

/*
COMPONENTE: AppRoutes

Define las direcciones disponibles.
*/
function AppRoutes() {

  const { usuario } = useAuth();

  return (
    <Routes>

      {/* Ruta de inicio de sesión. */}
      <Route
        path="/login"
        element={
          usuario
            ? <Navigate to="/dashboard" replace />
            : <Login />
        }
      />

      {/* Ruta protegida del Dashboard. */}
      <Route
        path="/dashboard"
        element={
          <RutaProtegida>
            <DashboardTemporal />
          </RutaProtegida>
        }
      />

      {/* Cualquier ruta desconocida vuelve al login. */}
      <Route
        path="*"
        element={<Navigate to="/login" replace />}
      />

    </Routes>
  );
}

/*
COMPONENTE PRINCIPAL: App

BrowserRouter activa la navegación.
AuthProvider comparte la autenticación.
*/
export default function App() {

  return (
    <BrowserRouter>

      <AuthProvider>
        <AppRoutes />
      </AuthProvider>

    </BrowserRouter>
  );
}
