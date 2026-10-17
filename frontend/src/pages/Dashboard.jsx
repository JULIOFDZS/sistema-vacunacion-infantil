/*
====================================================
 ARCHIVO: src/pages/Dashboard.jsx
 FUNCIÓN: Resumen general (GET /dashboard/resumen)
====================================================
*/

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  Syringe,
  CalendarClock,
  FileSpreadsheet,
  ClipboardList,
  ArrowRight,
} from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { mensajeError } from "../services/utilidades";
import { Alerta, Cargando, EncabezadoPagina } from "../components/ui";

function Tarjeta({ icono: Icono, titulo, valor, detalle, tono = "teal" }) {
  return (
    <div className="tarjeta-dato">
      <div className={`tarjeta-dato-icono tono-${tono}`}>
        <Icono size={22} />
      </div>
      <div>
        <small>{titulo}</small>
        <strong>{valor ?? 0}</strong>
        {detalle && <span>{detalle}</span>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { usuario, puedeEscribir } = useAuth();
  const [resumen, setResumen] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let activo = true;

    api
      .get("/dashboard/resumen")
      .then((r) => activo && setResumen(r.data))
      .catch((e) => activo && setError(mensajeError(e)));

    return () => {
      activo = false;
    };
  }, []);

  const primerNombre = usuario?.nombre?.split(" ")[0] || "";

  return (
    <>
      <EncabezadoPagina
        titulo={`Hola${primerNombre ? `, ${primerNombre}` : ""}`}
        subtitulo="Resumen administrativo de los registros de vacunación."
      />

      {error && <Alerta tipo="error">{error}</Alerta>}
      {!resumen && !error && <Cargando />}

      {resumen && (
        <>
          <section className="rejilla-tarjetas">
            <Tarjeta
              icono={Users}
              titulo="Pacientes"
              valor={resumen.pacientes?.total}
              detalle={`${resumen.pacientes?.sin_fecha_nacimiento ?? 0} sin fecha de nacimiento`}
            />
            <Tarjeta
              icono={Syringe}
              titulo="Dosis registradas"
              valor={resumen.aplicaciones?.no_anuladas}
              detalle={`${resumen.aplicaciones?.anuladas ?? 0} anuladas`}
              tono="azul"
            />
            <Tarjeta
              icono={CalendarClock}
              titulo="Dosis sin fecha"
              valor={resumen.aplicaciones?.sin_fecha}
              detalle={`${resumen.aplicaciones?.porcentaje_sin_fecha ?? 0}% de las registradas`}
              tono="ambar"
            />
            <Tarjeta
              icono={FileSpreadsheet}
              titulo="Origen SISVACU"
              valor={resumen.origen_registros?.sisvacu}
              detalle={`${resumen.origen_registros?.porcentaje_sisvacu ?? 0}% de las registradas`}
              tono="violeta"
            />
          </section>

          <section className="dos-columnas">
            <div className="panel">
              <h2>Calendario de referencia</h2>
              <dl className="lista-datos">
                <div>
                  <dt>Reglas totales</dt>
                  <dd>{resumen.calendario?.total_reglas ?? 0}</dd>
                </div>
                <div>
                  <dt>Activas</dt>
                  <dd>{resumen.calendario?.reglas_activas ?? 0}</dd>
                </div>
                <div>
                  <dt>Inactivas (sin validar)</dt>
                  <dd>{resumen.calendario?.reglas_inactivas ?? 0}</dd>
                </div>
              </dl>
              <Link to="/esquema" className="enlace-flecha">
                Ver calendario <ArrowRight size={16} />
              </Link>
            </div>

            <div className="panel">
              <h2>Equivalencias de vacunas</h2>
              <dl className="lista-datos">
                <div>
                  <dt>Registradas</dt>
                  <dd>{resumen.equivalencias?.total ?? 0}</dd>
                </div>
                <div>
                  <dt>Verificadas</dt>
                  <dd>{resumen.equivalencias?.verificadas ?? 0}</dd>
                </div>
                <div>
                  <dt>Pendientes</dt>
                  <dd>{resumen.equivalencias?.pendientes ?? 0}</dd>
                </div>
              </dl>
            </div>
          </section>

          <section className="accesos">
            <Link to="/pacientes" className="acceso">
              <ClipboardList size={22} />
              <div>
                <strong>Pacientes</strong>
                <span>Buscar, registrar y ver el historial</span>
              </div>
              <ArrowRight size={18} />
            </Link>

            {puedeEscribir && (
              <Link to="/importar" className="acceso">
                <FileSpreadsheet size={22} />
                <div>
                  <strong>Importar Excel</strong>
                  <span>Cargar el registro SISVACU</span>
                </div>
                <ArrowRight size={18} />
              </Link>
            )}
          </section>

          {resumen.advertencia && (
            <Alerta tipo="info">{resumen.advertencia}</Alerta>
          )}
        </>
      )}
    </>
  );
}
