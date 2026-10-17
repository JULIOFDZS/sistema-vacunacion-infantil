/*
====================================================
 ARCHIVO: src/services/utilidades.js
 FUNCIÓN: Funciones auxiliares compartidas
====================================================
*/

// Extrae un mensaje legible de un error de Axios/FastAPI.
export function mensajeError(error, porDefecto = "Ocurrió un error inesperado.") {
  if (!error.response) {
    return "No se pudo conectar con el servidor. Verifica que FastAPI esté funcionando.";
  }

  const detalle = error.response.data?.detail;

  if (typeof detalle === "string") return detalle;

  // Errores de validación de FastAPI (422): lista de objetos.
  if (Array.isArray(detalle)) {
    return detalle
      .map((d) => {
        const campo = Array.isArray(d.loc) ? d.loc.slice(1).join(".") : "";
        return campo ? `${campo}: ${d.msg}` : d.msg;
      })
      .join(" · ");
  }

  // Errores con estructura { mensaje, ... } (importaciones).
  if (detalle && typeof detalle === "object" && detalle.mensaje) {
    return detalle.mensaje;
  }

  if (error.response.status === 403) {
    return "Tu rol no permite realizar esta operación.";
  }

  return porDefecto;
}

// Formatea una fecha ISO (YYYY-MM-DD) como DD/MM/AAAA
// sin sufrir cambios de zona horaria.
export function formatearFecha(iso) {
  if (!iso) return "—";
  const [anio, mes, dia] = String(iso).slice(0, 10).split("-");
  if (!anio || !mes || !dia) return "—";
  return `${dia}/${mes}/${anio}`;
}

// Calcula la edad en meses a partir de la fecha de nacimiento.
export function edadEnMeses(fechaNacimiento) {
  if (!fechaNacimiento) return null;
  const [a, m, d] = fechaNacimiento.split("-").map(Number);
  const hoy = new Date();
  let meses = (hoy.getFullYear() - a) * 12 + (hoy.getMonth() + 1 - m);
  if (hoy.getDate() < d) meses -= 1;
  return Math.max(meses, 0);
}

// Texto de edad: "8 meses", "2 años 3 meses" o la edad reportada.
export function textoEdad(paciente) {
  const meses = edadEnMeses(paciente?.fecha_nacimiento);

  if (meses === null) {
    const reportada = paciente?.edad_reportada_anios;
    return reportada === null || reportada === undefined
      ? "—"
      : `${reportada} ${reportada === 1 ? "año" : "años"} (reportada)`;
  }

  if (meses < 24) return `${meses} ${meses === 1 ? "mes" : "meses"}`;

  const anios = Math.floor(meses / 12);
  const resto = meses % 12;
  const base = `${anios} años`;
  return resto ? `${base} ${resto} ${resto === 1 ? "mes" : "meses"}` : base;
}

// Convierte meses a un texto corto para el calendario.
export function textoMeses(meses) {
  if (meses === null || meses === undefined) return "—";
  if (meses === 0) return "Al nacer";
  if (meses < 24) return `${meses} ${meses === 1 ? "mes" : "meses"}`;
  const anios = meses / 12;
  return Number.isInteger(anios)
    ? `${anios} años`
    : `${Math.floor(anios)} años ${meses % 12} m`;
}

export const ETIQUETAS_ROL = {
  admin: "Administrador",
  operador: "Operador",
  visualizador: "Visualizador",
};

export const TIPOS_DOCUMENTO = {
  cedula: "Cédula",
  temporal_sisvacu: "Temporal SISVACU",
  sin_documento: "Sin documento",
  invalido: "Documento inválido",
};

export function textoAnios(n) {
  return `${n} ${n === 1 ? "año" : "años"}`;
}

export function capitalizar(texto) {
  return texto ? texto.charAt(0).toUpperCase() + texto.slice(1) : "";
}
