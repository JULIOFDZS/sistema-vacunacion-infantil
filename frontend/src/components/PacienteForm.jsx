/*
====================================================
 ARCHIVO: src/components/PacienteForm.jsx
 FUNCIÓN: Formulario para crear o editar un paciente
 - Crear:  POST /pacientes/        (admin y operador)
 - Editar: PUT  /pacientes/{id}    (solo admin)
====================================================
*/

import { useState } from "react";

import api from "../services/api";
import { mensajeError } from "../services/utilidades";
import { Alerta } from "./ui";

const hoyISO = () => new Date().toISOString().slice(0, 10);

// Convierte el formulario (todo texto) al formato del backend.
function aCarga(f) {
  const numero = (v) => (v === "" ? null : Number(v));

  return {
    nombres: f.nombres.trim(),
    apellidos: f.apellidos.trim(),
    fecha_nacimiento: f.fecha_nacimiento || null,
    origen_fecha_nacimiento: f.fecha_nacimiento
      ? f.origen_fecha_nacimiento || null
      : null,
    edad_reportada_anios: numero(f.edad_reportada_anios),
    sexo: f.sexo || null,
    nacimiento_prematuro:
      f.nacimiento_prematuro === ""
        ? null
        : f.nacimiento_prematuro === "si",
    semanas_gestacion: numero(f.semanas_gestacion),
    peso_nacimiento_gr: numero(f.peso_nacimiento_gr),
    observaciones: f.observaciones.trim() || null,
  };
}

function aFormulario(p) {
  return {
    nombres: p?.nombres ?? "",
    apellidos: p?.apellidos ?? "",
    fecha_nacimiento: p?.fecha_nacimiento ?? "",
    origen_fecha_nacimiento: p?.origen_fecha_nacimiento ?? "",
    edad_reportada_anios: p?.edad_reportada_anios ?? "",
    sexo: p?.sexo ?? "",
    nacimiento_prematuro:
      p?.nacimiento_prematuro === 1 || p?.nacimiento_prematuro === true
        ? "si"
        : p?.nacimiento_prematuro === 0 || p?.nacimiento_prematuro === false
          ? "no"
          : "",
    semanas_gestacion: p?.semanas_gestacion ?? "",
    peso_nacimiento_gr: p?.peso_nacimiento_gr ?? "",
    observaciones: p?.observaciones ?? "",
  };
}

export default function PacienteForm({ paciente, onGuardado, onCancelar }) {
  const editando = Boolean(paciente);
  const [f, setF] = useState(() => aFormulario(paciente));
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");

  const cambiar = (campo) => (e) =>
    setF((previo) => ({ ...previo, [campo]: e.target.value }));

  const enviar = async (e) => {
    e.preventDefault();
    setError("");
    setGuardando(true);

    try {
      const carga = aCarga(f);
      const respuesta = editando
        ? await api.put(`/pacientes/${paciente.id}`, carga)
        : await api.post("/pacientes/", carga);

      onGuardado(respuesta.data);
    } catch (err) {
      setError(mensajeError(err, "No se pudo guardar el paciente."));
    } finally {
      setGuardando(false);
    }
  };

  return (
    <form onSubmit={enviar} className="formulario">
      <div className="campos-2">
        <label className="campo">
          <span>Nombres *</span>
          <input
            value={f.nombres}
            onChange={cambiar("nombres")}
            minLength={2}
            maxLength={100}
            required
            autoFocus
          />
        </label>

        <label className="campo">
          <span>Apellidos *</span>
          <input
            value={f.apellidos}
            onChange={cambiar("apellidos")}
            minLength={2}
            maxLength={100}
            required
          />
        </label>
      </div>

      <div className="campos-2">
        <label className="campo">
          <span>Fecha de nacimiento</span>
          <input
            type="date"
            value={f.fecha_nacimiento}
            onChange={cambiar("fecha_nacimiento")}
            max={hoyISO()}
          />
        </label>

        <label className="campo">
          <span>Origen de la fecha</span>
          <select
            value={f.origen_fecha_nacimiento}
            onChange={cambiar("origen_fecha_nacimiento")}
            disabled={!f.fecha_nacimiento}
          >
            <option value="">Sin especificar</option>
            <option value="documento">Documento</option>
            <option value="carnet">Carnet de vacunación</option>
            <option value="informada">Informada por el tutor</option>
          </select>
        </label>
      </div>

      <div className="campos-2">
        <label className="campo">
          <span>Edad reportada (años)</span>
          <input
            type="number"
            min={0}
            max={6}
            value={f.edad_reportada_anios}
            onChange={cambiar("edad_reportada_anios")}
            placeholder="0 a 6"
          />
          <small>Útil si no se conoce la fecha exacta.</small>
        </label>

        <label className="campo">
          <span>Sexo</span>
          <select value={f.sexo} onChange={cambiar("sexo")}>
            <option value="">Sin especificar</option>
            <option value="femenino">Femenino</option>
            <option value="masculino">Masculino</option>
          </select>
        </label>
      </div>

      <div className="campos-3">
        <label className="campo">
          <span>Nacimiento prematuro</span>
          <select
            value={f.nacimiento_prematuro}
            onChange={cambiar("nacimiento_prematuro")}
          >
            <option value="">Sin dato</option>
            <option value="no">No</option>
            <option value="si">Sí</option>
          </select>
        </label>

        <label className="campo">
          <span>Semanas de gestación</span>
          <input
            type="number"
            min={22}
            max={42}
            value={f.semanas_gestacion}
            onChange={cambiar("semanas_gestacion")}
          />
        </label>

        <label className="campo">
          <span>Peso al nacer (g)</span>
          <input
            type="number"
            min={400}
            max={6000}
            value={f.peso_nacimiento_gr}
            onChange={cambiar("peso_nacimiento_gr")}
          />
        </label>
      </div>

      <label className="campo">
        <span>Observaciones</span>
        <textarea
          rows={3}
          value={f.observaciones}
          onChange={cambiar("observaciones")}
        />
      </label>

      {error && <Alerta tipo="error">{error}</Alerta>}

      <div className="formulario-acciones">
        <button type="button" className="btn btn-secundario" onClick={onCancelar}>
          Cancelar
        </button>
        <button type="submit" className="btn btn-primario" disabled={guardando}>
          {guardando
            ? "Guardando..."
            : editando
              ? "Guardar cambios"
              : "Registrar paciente"}
        </button>
      </div>
    </form>
  );
}
