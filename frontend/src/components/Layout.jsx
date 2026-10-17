/*
====================================================
 ARCHIVO: src/components/Layout.jsx
 FUNCIÓN: Estructura general (menú + contenido)
 - Escritorio: barra lateral.
 - Celular: barra inferior de navegación.
====================================================
*/

import { NavLink, Outlet } from "react-router-dom";
import {
  ShieldPlus,
  LayoutDashboard,
  Users,
  FileSpreadsheet,
  CalendarDays,
  UserCog,
  LogOut,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { ETIQUETAS_ROL } from "../services/utilidades";

export default function Layout() {
  const { usuario, cerrarSesion, esAdmin, puedeEscribir } = useAuth();

  // Las opciones visibles dependen del rol.
  const opciones = [
    { a: "/dashboard", texto: "Inicio", icono: LayoutDashboard },
    { a: "/pacientes", texto: "Pacientes", icono: Users },
    puedeEscribir && {
      a: "/importar",
      texto: "Importar",
      icono: FileSpreadsheet,
    },
    { a: "/esquema", texto: "Calendario", icono: CalendarDays },
    esAdmin && { a: "/usuarios", texto: "Usuarios", icono: UserCog },
  ].filter(Boolean);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <ShieldPlus size={28} />
          <span>VacunaControl</span>
        </div>

        <nav className="sidebar-nav" aria-label="Navegación principal">
          {opciones.map(({ a, texto, icono: Icono }) => (
            <NavLink
              key={a}
              to={a}
              className={({ isActive }) =>
                `nav-link${isActive ? " activo" : ""}`
              }
            >
              <Icono size={19} />
              <span>{texto}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="sidebar-user-datos">
            <strong>{usuario?.nombre}</strong>
            <small>{ETIQUETAS_ROL[usuario?.rol] || usuario?.rol}</small>
          </div>

          <button
            type="button"
            className="btn-icono"
            onClick={cerrarSesion}
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
          >
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      <div className="contenido-area">
        <header className="topbar-movil">
          <div className="sidebar-brand">
            <ShieldPlus size={24} />
            <span>VacunaControl</span>
          </div>

          <button
            type="button"
            className="btn-icono"
            onClick={cerrarSesion}
            aria-label="Cerrar sesión"
          >
            <LogOut size={19} />
          </button>
        </header>

        <main className="contenido">
          <Outlet />
        </main>
      </div>

      <nav className="bottom-nav" aria-label="Navegación principal">
        {opciones.map(({ a, texto, icono: Icono }) => (
          <NavLink
            key={a}
            to={a}
            className={({ isActive }) =>
              `bottom-link${isActive ? " activo" : ""}`
            }
          >
            <Icono size={21} />
            <span>{texto}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
