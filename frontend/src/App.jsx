/*
====================================================
 ARCHIVO: src/App.jsx
 FUNCIÓN: Administrar la navegación del sistema
====================================================
*/

import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Pacientes from "./pages/Pacientes";
import PacienteDetalle from "./pages/PacienteDetalle";
import Importar from "./pages/Importar";
import Esquema from "./pages/Esquema";
import Usuarios from "./pages/Usuarios";

import "./styles/App.css";

/*
COMPONENTE: RutaProtegida

Exige sesión iniciada y, opcionalmente, un permiso:
- "escritura": admin y operador.
- "admin": solo administrador.
Recuerda que el backend valida los permisos de verdad;
esto solo evita mostrar pantallas inútiles.
*/
function RutaProtegida({ children, requiere }) {
  const { usuario, esAdmin, puedeEscribir } = useAuth();

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  if (requiere === "admin" && !esAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  if (requiere === "escritura" && !puedeEscribir) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function AppRoutes() {
  const { usuario } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          usuario ? <Navigate to="/dashboard" replace /> : <Login />
        }
      />

      {/* Todas las pantallas internas comparten el Layout. */}
      <Route
        element={
          <RutaProtegida>
            <Layout />
          </RutaProtegida>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/pacientes" element={<Pacientes />} />
        <Route path="/pacientes/:id" element={<PacienteDetalle />} />
        <Route path="/esquema" element={<Esquema />} />

        <Route
          path="/importar"
          element={
            <RutaProtegida requiere="escritura">
              <Importar />
            </RutaProtegida>
          }
        />

        <Route
          path="/usuarios"
          element={
            <RutaProtegida requiere="admin">
              <Usuarios />
            </RutaProtegida>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
