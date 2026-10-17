/*
====================================================
 ARCHIVO: src/pages/PacienteDetalle.jsx
 FUNCIÓN: Ficha de un paciente
 - GET /historial/paciente/{id}
 - GET /pacientes/{id}/estado-vacunacion
====================================================
*/

import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Pencil, Syringe, IdCard } from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  capitalizar,
  formatearFecha,
  mensajeError,
  textoEdad,
  textoMeses,
  TIPOS_DOCUMENTO,
} from "../services/utilidades";
import {
  Alerta,
  Cargando,
  Insignia,
  Modal,
  Vacio,
} from "../components/ui";
import PacienteForm from "../components/PacienteForm";

const ESTADOS = {
  edad_exacta_desconocida: {
    tono: "ambar",
    texto: "Falta la fecha de nacimiento",
  },
  sin_esquema_activo: {
    tono: "gris",
    texto: "Calendario sin activar",
  },
  evaluacion_pendiente_validacion: {
    tono: "azul",
    texto: "Evaluación pendiente de validación",
  },
};

const ESTADO_REGISTRO = {
  registrada_con_fecha: { tono: "verde", texto: "Con fecha" },
  registrada_sin_fecha: { tono: "ambar", texto: "Sin fecha" },
  anulada: { tono: "rojo", texto: "Anulada" },
};

export default function PacienteDetalle() {
  const { id } = useParams();
  const { esAdmin } = useAuth();

  const [historial, setHistorial] = useState(null);
  const [estado, setEstado] = useState(null);
  // Registro completo (el historial solo trae datos resumidos).
  const [completo, setCompleto] = useState(null);
  const [error, setError] = useState("");
  const [editando, setEditando] = useState(false);
  const [soloVigentes, setSoloVigentes] = useState(true);

  const cargar = useCallback(async () => {
    setError("");

    try {
      const [h, e, c] = await Promise.all([
        api.get(`/historial/paciente/${id}`),
        api.get(`/pacientes/${id}/estado-vacunacion`),
        api.get(`/pacientes/${id}`),
      ]);
      setHistorial(h.data);
      setEstado(e.data);
      setCompleto(c.data);
    } catch (err) {
      setError(
        err.response?.status === 404
          ? "Paciente no encontrado."
          : mensajeError(err)
      );
    }
  }, [id]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargar();
  }, [cargar]);

  if (error) {
    return (
      <>
        <Link to="/pacientes" className="enlace-volver">
          <ArrowLeft size={17} /> Pacientes
        </Link>
        <Alerta tipo="error">{error}</Alerta>
      </>
    );
  }

  if (!historial || !estado || !completo) return <Cargando />;

  const p = historial.paciente;
  const aplicaciones = historial.aplicaciones || [];
  const mostradas = soloVigentes
    ? aplicaciones.filter((a) => !a.anulada)
    : aplicaciones;
  const infoEstado = ESTADOS[estado.estado];

  // Códigos de vacuna ya registrados (para marcar el calendario).
  const codigosAplicados = new Set(
    (estado.vacunas_aplicadas || []).map((v) => v.codigo)
  );

  return (
    <>
      <Link to="/pacientes" className="enlace-volver">
        <ArrowLeft size={17} /> Pacientes
      </Link>

      {/* Cabecera del paciente */}
      <section className="panel ficha">
        <span className="avatar avatar-grande" aria-hidden="true">
          {(p.nombres?.[0] || "?") + (p.apellidos?.[0] || "")}
        </span>

        <div className="ficha-datos">
          <h1>{p.nombre_completo}</h1>

          <div className="ficha-meta">
            <span>{textoEdad(p)}</span>
            <span>Nac.: {formatearFecha(p.fecha_nacimiento)}</span>
            {p.sexo && <span className="capitalizar">{p.sexo}</span>}
          </div>

          <div className="ficha-etiquetas">
            <Insignia tono={p.estado === "activo" ? "verde" : "gris"}>
              {capitalizar(p.estado)}
            </Insignia>
            {p.completitud === "minimo" && (
              <Insignia tono="ambar">Datos mínimos</Insignia>
            )}
          </div>
        </div>

        {esAdmin && (
          <button
            type="button"
            className="btn btn-secundario"
            onClick={() => setEditando(true)}
          >
            <Pencil size={16} /> Editar
          </button>
        )}
      </section>

      {/* Identificadores */}
      {historial.identificadores?.length > 0 && (
        <section className="panel">
          <h2>
            <IdCard size={18} /> Identificadores
          </h2>
          <ul className="etiquetas">
            {historial.identificadores.map((i) => (
              <li key={i.id}>
                <strong>{TIPOS_DOCUMENTO[i.tipo] || i.tipo}</strong> {i.numero}
                {!i.vigente && <em> (no vigente)</em>}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Estado de vacunación */}
      <section className="panel">
        <h2>Estado de vacunación</h2>

        <div className="ficha-etiquetas">
          {infoEstado && <Insignia tono={infoEstado.tono}>{infoEstado.texto}</Insignia>}
          <Insignia tono="gris">
            {estado.total_aplicaciones_registradas} dosis registradas
          </Insignia>
        </div>

        {!estado.evaluacion_clinica_validada && (
          <Alerta tipo="aviso">
            La evaluación clínica todavía no está validada: esta pantalla
            muestra registros y reglas por edad, pero no determina dosis
            pendientes ni esquemas completos.
          </Alerta>
        )}

        {estado.observaciones?.map((o, i) => (
          <p key={i} className="nota">
            {o}
          </p>
        ))}

        {estado.dosis_requeridas?.length > 0 && (
          <>
            <h3>Dosis del calendario según la edad</h3>
            <ul className="lista-dosis">
              {estado.dosis_requeridas.map((d) => (
                <li key={d.codigo}>
                  <div>
                    <strong>{d.nombre}</strong>
                    <small>
                      Desde {textoMeses(d.edad_minima_meses)}
                      {d.edad_recomendada_meses !== null &&
                        ` · recomendada ${textoMeses(d.edad_recomendada_meses)}`}
                    </small>
                  </div>
                  {codigosAplicados.has(d.codigo) ? (
                    <Insignia tono="verde">Registrada</Insignia>
                  ) : (
                    <Insignia tono="gris">Sin coincidencia</Insignia>
                  )}
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      {/* Historial de aplicaciones */}
      <section className="panel">
        <div className="panel-cabecera">
          <h2>
            <Syringe size={18} /> Historial de dosis
          </h2>

          {aplicaciones.some((a) => a.anulada) && (
            <label className="interruptor">
              <input
                type="checkbox"
                checked={soloVigentes}
                onChange={(e) => setSoloVigentes(e.target.checked)}
              />
              <span>Ocultar anuladas</span>
            </label>
          )}
        </div>

        {mostradas.length === 0 ? (
          <Vacio
            icono={Syringe}
            titulo="Sin dosis registradas"
            texto="Las dosis aparecerán al importar el Excel de SISVACU."
          />
        ) : (
          <ul className="lista-dosis">
            {mostradas.map((a) => {
              const reg = ESTADO_REGISTRO[a.estado_registro];
              return (
                <li key={a.id}>
                  <div>
                    <strong>{a.nombre_vacuna || a.codigo_vacuna}</strong>
                    <small>
                      {formatearFecha(a.fecha_aplicacion)}
                      {a.lote && ` · Lote ${a.lote}`}
                      {a.origen && ` · ${a.origen}`}
                    </small>
                    {a.anulada && a.motivo_anulacion && (
                      <small>Motivo: {a.motivo_anulacion}</small>
                    )}
                  </div>
                  {reg && <Insignia tono={reg.tono}>{reg.texto}</Insignia>}
                </li>
              );
            })}
          </ul>
        )}

        {historial.observacion && <p className="nota">{historial.observacion}</p>}
      </section>

      {completo.observaciones && (
        <section className="panel">
          <h2>Observaciones</h2>
          <p className="nota">{completo.observaciones}</p>
        </section>
      )}

      {editando && (
        <Modal titulo="Editar paciente" onCerrar={() => setEditando(false)}>
          <PacienteForm
            paciente={completo}
            onCancelar={() => setEditando(false)}
            onGuardado={() => {
              setEditando(false);
              cargar();
            }}
          />
        </Modal>
      )}
    </>
  );
}
