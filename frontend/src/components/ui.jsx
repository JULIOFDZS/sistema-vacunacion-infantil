/*
====================================================
 ARCHIVO: src/components/ui.jsx
 FUNCIÓN: Piezas visuales reutilizables
====================================================
*/

import { useEffect } from "react";
import { AlertTriangle, CheckCircle2, Info, Loader2, X } from "lucide-react";

export function Cargando({ texto = "Cargando..." }) {
  return (
    <div className="cargando" role="status">
      <Loader2 className="girar" size={22} />
      <span>{texto}</span>
    </div>
  );
}

// tipo: "error" | "exito" | "aviso" | "info"
export function Alerta({ tipo = "info", children }) {
  const Icono =
    tipo === "error" || tipo === "aviso"
      ? AlertTriangle
      : tipo === "exito"
        ? CheckCircle2
        : Info;

  return (
    <div
      className={`alerta alerta-${tipo}`}
      role={tipo === "error" ? "alert" : "status"}
    >
      <Icono size={18} />
      <div>{children}</div>
    </div>
  );
}

export function EncabezadoPagina({ titulo, subtitulo, acciones }) {
  return (
    <div className="pagina-encabezado">
      <div>
        <h1>{titulo}</h1>
        {subtitulo && <p>{subtitulo}</p>}
      </div>
      {acciones && <div className="pagina-acciones">{acciones}</div>}
    </div>
  );
}

export function Insignia({ tono = "gris", children }) {
  return <span className={`insignia insignia-${tono}`}>{children}</span>;
}

export function Vacio({ icono: Icono, titulo, texto }) {
  return (
    <div className="vacio">
      {Icono && <Icono size={34} />}
      <strong>{titulo}</strong>
      {texto && <p>{texto}</p>}
    </div>
  );
}

// Ventana modal accesible (se cierra con Escape o al tocar fuera).
export function Modal({ titulo, onCerrar, children }) {
  useEffect(() => {
    const alTeclear = (e) => e.key === "Escape" && onCerrar();
    document.addEventListener("keydown", alTeclear);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", alTeclear);
      document.body.style.overflow = "";
    };
  }, [onCerrar]);

  return (
    <div className="modal-fondo" onMouseDown={onCerrar}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="modal-cabecera">
          <h2>{titulo}</h2>
          <button
            type="button"
            className="btn-icono"
            onClick={onCerrar}
            aria-label="Cerrar"
          >
            <X size={19} />
          </button>
        </div>
        <div className="modal-cuerpo">{children}</div>
      </div>
    </div>
  );
}
