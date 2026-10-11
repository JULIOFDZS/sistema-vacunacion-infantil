
/*
====================================================
 ARCHIVO: src/pages/Login.jsx
 FUNCIÓN: Mostrar el formulario de inicio de sesión
====================================================
*/

// useState permite manejar los campos del formulario.
import { useState } from "react";

// useNavigate permite cambiar de página.
import { useNavigate } from "react-router-dom";

// Importamos iconos para mejorar el diseño.
import {
  ShieldPlus,
  Mail,
  LockKeyhole,
  Eye,
  EyeOff,
  ArrowRight,
} from "lucide-react";

// Importamos la función de autenticación.
import { useAuth } from "../context/AuthContext";

// Importamos los estilos visuales del login.
import "../styles/Login.css";

export default function Login() {

  // Permite navegar hacia el Dashboard.
  const navigate = useNavigate();

  // Obtenemos la función de login y el estado de carga.
  const { iniciarSesion, cargando } = useAuth();

  // Guarda el correo escrito por el usuario.
  const [email, setEmail] = useState("");

  // Guarda temporalmente la contraseña.
  const [password, setPassword] = useState("");

  // Controla si la contraseña se muestra o se oculta.
  const [mostrarPassword, setMostrarPassword] =
    useState(false);

  // Guarda los mensajes de error.
  const [error, setError] = useState("");

  /*
  FUNCIÓN: manejarEnvio

  Se ejecuta cuando el usuario presiona
  el botón "Iniciar sesión".
  */
  const manejarEnvio = async (evento) => {

    // Evita que el navegador recargue la página.
    evento.preventDefault();

    // Limpiamos los errores anteriores.
    setError("");

    try {

      // Enviamos las credenciales a FastAPI.
      await iniciarSesion(email.trim(), password);

      // Si el login funciona, abrimos el Dashboard.
      navigate("/dashboard", { replace: true });

    } catch (err) {

      // Si FastAPI devuelve 401, las credenciales fallaron.
      if (err.response?.status === 401) {

        setError(
          "Correo electrónico o contraseña incorrectos."
        );

      } else {

        // Otros errores: servidor apagado, CORS, etc.
        setError(
          "No se pudo iniciar sesión. " +
          "Verifica que FastAPI esté funcionando."
        );

      }
    }
  };

  // JSX: estructura visual de la pantalla.
  return (
    <main className="login-page">

      {/* PANEL IZQUIERDO: información del sistema */}
      <section className="login-info">

        {/* Logo y nombre */}
        <div className="login-brand">
          <ShieldPlus size={35} />
          <span>VacunaControl</span>
        </div>

        {/* Presentación del sistema */}
        <div className="login-info-content">

          <span className="login-tag">
            GESTIÓN DE SALUD INFANTIL
          </span>

          <h1>
            Protegiendo el futuro,
            <span> una vacuna a la vez.</span>
          </h1>

          <p>
            Plataforma de gestión y seguimiento
            de registros de vacunación infantil.
          </p>

          {/* Información de seguridad */}
          <div className="login-info-card">

            <ShieldPlus size={25} />

            <div>
              <strong>Acceso protegido</strong>

              <p>
                Acceso mediante usuarios autenticados
                y permisos definidos por rol.
              </p>
            </div>

          </div>
        </div>

        <p className="login-footer">
          Sistema de Vacunación Infantil
        </p>

      </section>

      {/* PANEL DERECHO: formulario */}
      <section className="login-form-section">

        <div className="login-form-container">

          {/* Logo visible en dispositivos móviles */}
          <div className="login-mobile-brand">
            <ShieldPlus size={30} />
            <span>VacunaControl</span>
          </div>

          {/* Título del formulario */}
          <div className="login-heading">
            <h2>Bienvenido de nuevo</h2>

            <p>
              Ingresa tus credenciales para continuar.
            </p>
          </div>

          {/* Formulario de inicio de sesión */}
          <form onSubmit={manejarEnvio}>

            {/* CAMPO: CORREO ELECTRÓNICO */}
            <div className="login-field">

              <label htmlFor="email">
                Correo electrónico
              </label>

              <div className="login-input-wrapper">

                <Mail size={19} />

                <input
                  id="email"
                  type="email"
                  placeholder="usuario@ejemplo.com"

                  // Valor guardado en el estado.
                  value={email}

                  // Actualiza el correo al escribir.
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }

                  autoComplete="username"
                  required
                />

              </div>
            </div>

            {/* CAMPO: CONTRASEÑA */}
            <div className="login-field">

              <label htmlFor="password">
                Contraseña
              </label>

              <div className="login-input-wrapper">

                <LockKeyhole size={19} />

                <input
                  id="password"

                  // Cambia entre texto visible y oculto.
                  type={
                    mostrarPassword
                      ? "text"
                      : "password"
                  }

                  placeholder="Ingresa tu contraseña"
                  value={password}

                  // Actualiza la contraseña al escribir.
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }

                  autoComplete="current-password"
                  required
                />

                {/* Botón para mostrar u ocultar contraseña */}
                <button
                  type="button"
                  className="login-eye"

                  onClick={() =>
                    setMostrarPassword(!mostrarPassword)
                  }

                  aria-label={
                    mostrarPassword
                      ? "Ocultar contraseña"
                      : "Mostrar contraseña"
                  }
                >

                  {mostrarPassword
                    ? <EyeOff size={19} />
                    : <Eye size={19} />
                  }

                </button>

              </div>
            </div>

            {/* Mostramos errores solamente si existen */}
            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            {/* BOTÓN PARA INICIAR SESIÓN */}
            <button
              type="submit"
              className="login-submit"

              // Evita múltiples solicitudes simultáneas.
              disabled={cargando}
            >

              {cargando
                ? "Verificando..."
                : "Iniciar sesión"
              }

              {!cargando && <ArrowRight size={19} />}

            </button>

          </form>

          <p className="login-security-note">
            Acceso exclusivo para personal autorizado.
          </p>

        </div>
      </section>

    </main>
  );
}
