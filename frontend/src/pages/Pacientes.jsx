/*
====================================================
 ARCHIVO: src/pages/Pacientes.jsx
 FUNCIÓN: Listar, buscar y registrar pacientes
 - GET /pacientes/
 - GET /pacientes/buscar?nombre=
====================================================
*/

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search, Users, ChevronRight } from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { mensajeError, textoEdad } from "../services/utilidades";
import {
  Alerta,
  Cargando,
  EncabezadoPagina,
  Insignia,
  Modal,
  Vacio,
} from "../components/ui";
import PacienteForm from "../components/PacienteForm";

const POR_PAGINA = 25;

export default function Pacientes() {
  const navigate = useNavigate();
  const { puedeEscribir } = useAuth();

  const [pacientes, setPacientes] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [pagina, setPagina] = useState(1);
  const [creando, setCreando] = useState(false);

  // Carga la lista completa o el resultado de la búsqueda
  // (con una pequeña espera mientras la persona escribe).
  useEffect(() => {
    let activo = true;
    const texto = busqueda.trim();

    const temporizador = setTimeout(
      () => {
        const peticion =
          texto.length >= 2
            ? api.get("/pacientes/buscar", { params: { nombre: texto } })
            : api.get("/pacientes/");

        peticion
          .then((r) => {
            if (!activo) return;
            setPacientes(r.data);
            setError("");
            setPagina(1);
          })
          .catch((e) => activo && setError(mensajeError(e)));
      },
      texto ? 300 : 0
    );

    return () => {
      activo = false;
      clearTimeout(temporizador);
    };
  }, [busqueda]);

  const total = pacientes?.length ?? 0;
  const visibles = pacientes?.slice(0, pagina * POR_PAGINA) ?? [];

  return (
    <>
      <EncabezadoPagina
        titulo="Pacientes"
        subtitulo="Niños, jóvenes y adultos registrados en la clínica."
        acciones={
          puedeEscribir && (
            <button
              type="button"
              className="btn btn-primario"
              onClick={() => setCreando(true)}
            >
              <Plus size={18} /> Nuevo paciente
            </button>
          )
        }
      />

      <div className="buscador">
        <Search size={19} />
        <input
          type="search"
          placeholder="Buscar por nombre o apellido"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          aria-label="Buscar paciente"
        />
      </div>

      {error && <Alerta tipo="error">{error}</Alerta>}
      {!pacientes && !error && <Cargando />}

      {pacientes && total === 0 && (
        <Vacio
          icono={Users}
          titulo="No se encontraron pacientes"
          texto={
            busqueda
              ? "Prueba con otro nombre o apellido."
              : "Registra el primero o importa el Excel de SISVACU."
          }
        />
      )}

      {total > 0 && (
        <>
          <p className="contador">
            {total} {total === 1 ? "paciente" : "pacientes"}
          </p>

          <ul className="lista-filas">
            {visibles.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  className="fila-paciente"
                  onClick={() => navigate(`/pacientes/${p.id}`)}
                >
                  <span className="avatar" aria-hidden="true">
                    {(p.nombres?.[0] || "?") + (p.apellidos?.[0] || "")}
                  </span>

                  <span className="fila-paciente-texto">
                    <strong>
                      {p.apellidos}, {p.nombres}
                    </strong>
                    <small>{textoEdad(p)}</small>
                  </span>

                  {p.completitud === "minimo" && (
                    <Insignia tono="ambar">Datos mínimos</Insignia>
                  )}

                  <ChevronRight size={18} className="fila-flecha" />
                </button>
              </li>
            ))}
          </ul>

          {visibles.length < total && (
            <button
              type="button"
              className="btn btn-secundario btn-centrado"
              onClick={() => setPagina((n) => n + 1)}
            >
              Mostrar más ({total - visibles.length} restantes)
            </button>
          )}
        </>
      )}

      {creando && (
        <Modal titulo="Nuevo paciente" onCerrar={() => setCreando(false)}>
          <PacienteForm
            onCancelar={() => setCreando(false)}
            onGuardado={(nuevo) => {
              setCreando(false);
              navigate(`/pacientes/${nuevo.id}`);
            }}
          />
        </Modal>
      )}
    </>
  );
}
