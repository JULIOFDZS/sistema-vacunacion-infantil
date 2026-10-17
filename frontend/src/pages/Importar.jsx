/*
====================================================
 ARCHIVO: src/pages/Importar.jsx
 FUNCIÓN: Cargar el Excel de SISVACU en dos pasos
 1) POST /importaciones/sisvacu/vista-previa
    (revisa el archivo, no guarda nada)
 2) POST /importaciones/sisvacu/confirmar
    (guarda y vincula con los pacientes existentes
     según su documento)
====================================================
*/

import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  RotateCcw,
} from "lucide-react";

import api from "../services/api";
import {
  mensajeError,
  textoAnios,
  TIPOS_DOCUMENTO,
} from "../services/utilidades";
import {
  Alerta,
  Cargando,
  EncabezadoPagina,
  Insignia,
} from "../components/ui";

const TONO_FILA = { ok: "verde", advertencia: "ambar", error: "rojo" };

export default function Importar() {
  const entradaArchivo = useRef(null);

  const [archivo, setArchivo] = useState(null);
  const [vistaPrevia, setVistaPrevia] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [arrastrando, setArrastrando] = useState(false);
  const [filtro, setFiltro] = useState("todas");

  const reiniciar = () => {
    setArchivo(null);
    setVistaPrevia(null);
    setResultado(null);
    setError("");
    setFiltro("todas");
    if (entradaArchivo.current) entradaArchivo.current.value = "";
  };

  const enviarArchivo = (ruta, f) => {
    const datos = new FormData();
    datos.append("archivo", f);
    return api.post(ruta, datos, { timeout: 120000 });
  };

  // Paso 1: elegir el archivo y pedir la vista previa.
  const elegirArchivo = async (f) => {
    if (!f) return;

    reiniciar();

    if (!f.name.toLowerCase().endsWith(".xlsx")) {
      setError("Solo se permiten archivos .xlsx");
      return;
    }

    setArchivo(f);
    setCargando(true);

    try {
      const r = await enviarArchivo("/importaciones/sisvacu/vista-previa", f);
      setVistaPrevia(r.data);
    } catch (e) {
      setError(mensajeError(e, "No se pudo leer el archivo."));
      setArchivo(null);
    } finally {
      setCargando(false);
    }
  };

  // Paso 2: confirmar y guardar en la base de datos.
  const confirmar = async () => {
    setCargando(true);
    setError("");

    try {
      const r = await enviarArchivo("/importaciones/sisvacu/confirmar", archivo);
      setResultado(r.data);
      setVistaPrevia(null);
    } catch (e) {
      const detalle = e.response?.data?.detail;
      let texto = mensajeError(e, "No se pudo guardar la importación.");

      if (detalle?.filas?.length) {
        texto += ` Filas: ${detalle.filas.join(", ")}.`;
      }

      setError(texto);
    } finally {
      setCargando(false);
    }
  };

  const filas = vistaPrevia?.filas ?? [];
  const filasVisibles =
    filtro === "todas" ? filas : filas.filter((f) => f.estado === filtro);

  const sinDocumento = filas.filter(
    (f) => f.tipo_documento === "sin_documento"
  ).length;

  // El backend rechaza la confirmación si hay filas con error
  // o pacientes sin documento; lo avisamos antes de intentarlo.
  const puedeConfirmar =
    vistaPrevia?.valido &&
    vistaPrevia.filas_error === 0 &&
    sinDocumento === 0 &&
    filas.length > 0;

  return (
    <>
      <EncabezadoPagina
        titulo="Importar Excel"
        subtitulo="Carga el registro de SISVACU: los pacientes se vinculan por su documento y se agregan sus dosis."
      />

      {error && <Alerta tipo="error">{error}</Alerta>}

      {/* Resultado final */}
      {resultado && (
        <section className="panel">
          <Alerta tipo="exito">{resultado.mensaje}</Alerta>

          <dl className="lista-datos lista-datos-grande">
            <div>
              <dt>Filas procesadas</dt>
              <dd>{resultado.filas_procesadas}</dd>
            </div>
            <div>
              <dt>Pacientes nuevos</dt>
              <dd>{resultado.pacientes_creados}</dd>
            </div>
            <div>
              <dt>Pacientes ya existentes</dt>
              <dd>{resultado.pacientes_actualizados}</dd>
            </div>
            <div>
              <dt>Dosis agregadas</dt>
              <dd>{resultado.aplicaciones_creadas}</dd>
            </div>
            <div>
              <dt>Dosis ya registradas</dt>
              <dd>{resultado.aplicaciones_ya_existentes}</dd>
            </div>
            <div>
              <dt>Vacunas nuevas en catálogo</dt>
              <dd>{resultado.vacunas_creadas}</dd>
            </div>
          </dl>

          <div className="formulario-acciones">
            <button type="button" className="btn btn-secundario" onClick={reiniciar}>
              <RotateCcw size={16} /> Importar otro archivo
            </button>
            <Link to="/pacientes" className="btn btn-primario">
              Ver pacientes
            </Link>
          </div>
        </section>
      )}

      {/* Selector de archivo */}
      {!vistaPrevia && !resultado && !cargando && (
        <label
          className={`zona-carga${arrastrando ? " arrastrando" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setArrastrando(true);
          }}
          onDragLeave={() => setArrastrando(false)}
          onDrop={(e) => {
            e.preventDefault();
            setArrastrando(false);
            elegirArchivo(e.dataTransfer.files?.[0]);
          }}
        >
          <UploadCloud size={40} />
          <strong>Toca para elegir el Excel o arrástralo aquí</strong>
          <span>Formato .xlsx exportado de SISVACU</span>
          <input
            ref={entradaArchivo}
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onChange={(e) => elegirArchivo(e.target.files?.[0])}
          />
        </label>
      )}

      {cargando && (
        <Cargando
          texto={vistaPrevia ? "Guardando importación..." : "Revisando el archivo..."}
        />
      )}

      {/* Vista previa */}
      {vistaPrevia && !cargando && (
        <>
          <section className="panel">
            <div className="archivo-nombre">
              <FileSpreadsheet size={20} />
              <strong>{vistaPrevia.archivo}</strong>
            </div>

            {!vistaPrevia.valido ? (
              <Alerta tipo="error">
                El archivo no tiene el formato esperado:{" "}
                {vistaPrevia.errores?.join(" · ")}
              </Alerta>
            ) : (
              <div className="rejilla-mini">
                <div>
                  <strong>{vistaPrevia.total_filas}</strong>
                  <span>Filas</span>
                </div>
                <div className="tono-verde">
                  <strong>{vistaPrevia.filas_ok}</strong>
                  <span>Correctas</span>
                </div>
                <div className="tono-ambar">
                  <strong>{vistaPrevia.filas_advertencia}</strong>
                  <span>Con advertencia</span>
                </div>
                <div className="tono-rojo">
                  <strong>{vistaPrevia.filas_error}</strong>
                  <span>Con error</span>
                </div>
              </div>
            )}

            {vistaPrevia.valido && vistaPrevia.columnas_vacunas?.length > 0 && (
              <p className="nota">
                Vacunas detectadas ({vistaPrevia.columnas_vacunas.length}):{" "}
                {vistaPrevia.columnas_vacunas.join(", ")}
              </p>
            )}

            {vistaPrevia.valido && vistaPrevia.filas_error > 0 && (
              <Alerta tipo="error">
                Hay filas con errores. Corrígelas en el Excel y vuelve a subirlo:
                no se puede confirmar así.
              </Alerta>
            )}

            {vistaPrevia.valido && sinDocumento > 0 && (
              <Alerta tipo="aviso">
                {sinDocumento}{" "}
                {sinDocumento === 1 ? "paciente no tiene" : "pacientes no tienen"}{" "}
                documento. Sin documento no se pueden vincular y la importación
                se detendría para evitar duplicados.
              </Alerta>
            )}

            <div className="formulario-acciones">
              <button type="button" className="btn btn-secundario" onClick={reiniciar}>
                Cancelar
              </button>
              <button
                type="button"
                className="btn btn-primario"
                onClick={confirmar}
                disabled={!puedeConfirmar}
              >
                <CheckCircle2 size={17} /> Confirmar importación
              </button>
            </div>
          </section>

          {vistaPrevia.valido && (
            <section className="panel">
              <div className="panel-cabecera">
                <h2>Filas del archivo</h2>

                <select
                  value={filtro}
                  onChange={(e) => setFiltro(e.target.value)}
                  aria-label="Filtrar filas"
                >
                  <option value="todas">Todas</option>
                  <option value="ok">Correctas</option>
                  <option value="advertencia">Con advertencia</option>
                  <option value="error">Con error</option>
                </select>
              </div>

              <ul className="lista-filas-import">
                {filasVisibles.map((f) => (
                  <li key={f.fila}>
                    <div className="import-fila-cabecera">
                      <strong>
                        {f.apellidos}, {f.nombres}
                      </strong>
                      <Insignia tono={TONO_FILA[f.estado] || "gris"}>
                        Fila {f.fila}
                      </Insignia>
                    </div>

                    <small>
                      {TIPOS_DOCUMENTO[f.tipo_documento] || f.tipo_documento}
                      {f.documento && `: ${f.documento}`}
                      {f.edad !== null && f.edad !== undefined && ` · ${textoAnios(f.edad)}`}
                      {` · ${f.dosis_aplicadas?.length ?? 0} dosis`}
                    </small>

                    {[...(f.errores || []), ...(f.advertencias || [])].map((m, i) => (
                      <small
                        key={i}
                        className={i < (f.errores?.length || 0) ? "texto-error" : "texto-aviso"}
                      >
                        {m}
                      </small>
                    ))}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </>
  );
}
