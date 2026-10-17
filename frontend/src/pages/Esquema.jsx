/*
====================================================
 ARCHIVO: src/pages/Esquema.jsx
 FUNCIÓN: Calendario de vacunación de referencia
 - GET /esquema/                 (todos los roles)
 - PUT /esquema/{id}/estado      (solo admin)
 - POST /esquema/cargar-inicial  (solo admin)
====================================================
*/

import { useCallback, useEffect, useState } from "react";
import { CalendarDays, DownloadCloud } from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { mensajeError, textoMeses } from "../services/utilidades";
import {
  Alerta,
  Cargando,
  EncabezadoPagina,
  Insignia,
  Vacio,
} from "../components/ui";

export default function Esquema() {
  const { esAdmin } = useAuth();

  const [reglas, setReglas] = useState(null);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [soloActivas, setSoloActivas] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const r = await api.get("/esquema/");
      setReglas(r.data);
      setError("");
    } catch (e) {
      setError(mensajeError(e));
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargar();
  }, [cargar]);

  const cargarInicial = async () => {
    setOcupado(true);
    setAviso("");
    setError("");

    try {
      const r = await api.post("/esquema/cargar-inicial");
      setAviso(
        r.data?.mensaje ||
          "Se cargó el calendario preliminar. Las reglas quedan inactivas hasta validarlas."
      );
      await cargar();
    } catch (e) {
      setError(mensajeError(e));
    } finally {
      setOcupado(false);
    }
  };

  const cambiarEstado = async (regla) => {
    const nuevo = !regla.activa;

    // Activar una regla es una decisión clínica: pedimos confirmación.
    if (
      nuevo &&
      !window.confirm(
        `¿Activar "${regla.nombre_dosis}"? Solo debe activarse si fue verificada por personal competente.`
      )
    ) {
      return;
    }

    try {
      await api.put(`/esquema/${regla.id}/estado`, null, {
        params: { activa: nuevo },
      });
      setReglas((lista) =>
        lista.map((r) => (r.id === regla.id ? { ...r, activa: nuevo } : r))
      );
    } catch (e) {
      setError(mensajeError(e));
    }
  };

  const visibles = reglas?.filter((r) => !soloActivas || r.activa) ?? [];

  return (
    <>
      <EncabezadoPagina
        titulo="Calendario de vacunación"
        subtitulo="Reglas de referencia por edad. Las reglas preliminares deben validarse antes de usarse."
        acciones={
          esAdmin && (
            <button
              type="button"
              className="btn btn-secundario"
              onClick={cargarInicial}
              disabled={ocupado}
            >
              <DownloadCloud size={17} /> Cargar calendario inicial
            </button>
          )
        }
      />

      {error && <Alerta tipo="error">{error}</Alerta>}
      {aviso && <Alerta tipo="exito">{aviso}</Alerta>}
      {!reglas && !error && <Cargando />}

      {reglas && reglas.length === 0 && (
        <Vacio
          icono={CalendarDays}
          titulo="Todavía no hay reglas"
          texto={
            esAdmin
              ? "Usa «Cargar calendario inicial» para cargar las reglas preliminares."
              : "Un administrador debe cargar el calendario."
          }
        />
      )}

      {reglas?.length > 0 && (
        <>
          <label className="interruptor">
            <input
              type="checkbox"
              checked={soloActivas}
              onChange={(e) => setSoloActivas(e.target.checked)}
            />
            <span>Mostrar solo reglas activas</span>
          </label>

          <ul className="lista-filas">
            {visibles.map((r) => (
              <li key={r.id} className="fila-regla">
                <div className="fila-regla-texto">
                  <strong>{r.nombre_dosis}</strong>
                  <small>
                    {r.codigo_vacuna} · desde {textoMeses(r.edad_minima_meses)}
                    {r.edad_recomendada_meses !== null &&
                      ` · recomendada ${textoMeses(r.edad_recomendada_meses)}`}
                    {r.edad_maxima_meses !== null &&
                      ` · hasta ${textoMeses(r.edad_maxima_meses)}`}
                  </small>
                  {r.observaciones && <small>{r.observaciones}</small>}
                </div>

                <div className="fila-regla-estado">
                  <Insignia tono={r.activa ? "verde" : "gris"}>
                    {r.activa ? "Activa" : "Inactiva"}
                  </Insignia>

                  {esAdmin && (
                    <button
                      type="button"
                      className="btn btn-chico btn-secundario"
                      onClick={() => cambiarEstado(r)}
                    >
                      {r.activa ? "Desactivar" : "Activar"}
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}
