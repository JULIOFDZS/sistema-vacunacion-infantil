/*
====================================================
 ARCHIVO: src/pages/Usuarios.jsx
 FUNCIÓN: Administración de usuarios (solo admin)
 - GET  /usuarios/
 - POST /usuarios/
 - PUT  /usuarios/{id}/estado
====================================================
*/

import { useCallback, useEffect, useState } from "react";
import { UserPlus } from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { ETIQUETAS_ROL, mensajeError } from "../services/utilidades";
import {
  Alerta,
  Cargando,
  EncabezadoPagina,
  Insignia,
  Modal,
} from "../components/ui";

function FormularioUsuario({ onCreado, onCancelar }) {
  const [f, setF] = useState({
    nombre: "",
    email: "",
    password: "",
    rol: "operador",
  });
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  const cambiar = (campo) => (e) =>
    setF((previo) => ({ ...previo, [campo]: e.target.value }));

  const enviar = async (e) => {
    e.preventDefault();
    setError("");
    setGuardando(true);

    try {
      await api.post("/usuarios/", {
        ...f,
        nombre: f.nombre.trim(),
        email: f.email.trim(),
      });
      onCreado();
    } catch (err) {
      setError(mensajeError(err, "No se pudo crear el usuario."));
    } finally {
      setGuardando(false);
    }
  };

  return (
    <form onSubmit={enviar} className="formulario">
      <label className="campo">
        <span>Nombre completo *</span>
        <input
          value={f.nombre}
          onChange={cambiar("nombre")}
          minLength={2}
          maxLength={150}
          required
          autoFocus
        />
      </label>

      <label className="campo">
        <span>Correo electrónico *</span>
        <input
          type="email"
          value={f.email}
          onChange={cambiar("email")}
          autoComplete="off"
          required
        />
      </label>

      <label className="campo">
        <span>Contraseña inicial *</span>
        <input
          type="password"
          value={f.password}
          onChange={cambiar("password")}
          minLength={12}
          maxLength={128}
          autoComplete="new-password"
          required
        />
        <small>Mínimo 12 caracteres.</small>
      </label>

      <label className="campo">
        <span>Rol</span>
        <select value={f.rol} onChange={cambiar("rol")}>
          <option value="operador">Operador (registra y importa)</option>
          <option value="visualizador">Visualizador (solo consulta)</option>
        </select>
      </label>

      {error && <Alerta tipo="error">{error}</Alerta>}

      <div className="formulario-acciones">
        <button type="button" className="btn btn-secundario" onClick={onCancelar}>
          Cancelar
        </button>
        <button type="submit" className="btn btn-primario" disabled={guardando}>
          {guardando ? "Creando..." : "Crear usuario"}
        </button>
      </div>
    </form>
  );
}

export default function Usuarios() {
  const { usuario: yo } = useAuth();

  const [usuarios, setUsuarios] = useState(null);
  const [error, setError] = useState("");
  const [creando, setCreando] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const r = await api.get("/usuarios/");
      setUsuarios(r.data);
      setError("");
    } catch (e) {
      setError(mensajeError(e));
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargar();
  }, [cargar]);

  const cambiarEstado = async (u) => {
    try {
      const r = await api.put(`/usuarios/${u.id}/estado`, {
        activo: !u.activo,
      });
      setUsuarios((lista) =>
        lista.map((x) => (x.id === u.id ? r.data : x))
      );
    } catch (e) {
      setError(mensajeError(e));
    }
  };

  return (
    <>
      <EncabezadoPagina
        titulo="Usuarios"
        subtitulo="Personas con acceso al sistema y su rol."
        acciones={
          <button
            type="button"
            className="btn btn-primario"
            onClick={() => setCreando(true)}
          >
            <UserPlus size={18} /> Nuevo usuario
          </button>
        }
      />

      {error && <Alerta tipo="error">{error}</Alerta>}
      {!usuarios && !error && <Cargando />}

      {usuarios && (
        <ul className="lista-filas">
          {usuarios.map((u) => (
            <li key={u.id} className="fila-regla">
              <div className="fila-regla-texto">
                <strong>{u.nombre}</strong>
                <small>{u.email}</small>
              </div>

              <div className="fila-regla-estado">
                <Insignia tono={u.rol === "admin" ? "violeta" : "azul"}>
                  {ETIQUETAS_ROL[u.rol] || u.rol}
                </Insignia>
                <Insignia tono={u.activo ? "verde" : "gris"}>
                  {u.activo ? "Activo" : "Deshabilitado"}
                </Insignia>

                {u.id !== yo?.id && u.rol !== "admin" && (
                  <button
                    type="button"
                    className="btn btn-chico btn-secundario"
                    onClick={() => cambiarEstado(u)}
                  >
                    {u.activo ? "Deshabilitar" : "Habilitar"}
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {creando && (
        <Modal titulo="Nuevo usuario" onCerrar={() => setCreando(false)}>
          <FormularioUsuario
            onCancelar={() => setCreando(false)}
            onCreado={() => {
              setCreando(false);
              cargar();
            }}
          />
        </Modal>
      )}
    </>
  );
}
