/*
  Service worker mínimo de VacunaControl.

  - Guarda en caché la "carcasa" de la app (HTML, JS, CSS, íconos)
    para que abra rápido y funcione la instalación como PWA.
  - NUNCA guarda respuestas de la API: los datos de pacientes son
    sensibles y siempre deben pedirse al servidor.
*/

const CACHE = "vacunacontrol-v1";

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(["/", "/manifest.webmanifest"]))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches
      .keys()
      .then((claves) =>
        Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (evento) => {
  const peticion = evento.request;
  const url = new URL(peticion.url);

  // Solo recursos propios y de lectura; la API (otro origen) pasa directo.
  if (peticion.method !== "GET" || url.origin !== self.location.origin) return;

  // Navegación: red primero, con la carcasa en caché si no hay conexión.
  if (peticion.mode === "navigate") {
    evento.respondWith(fetch(peticion).catch(() => caches.match("/")));
    return;
  }

  // Archivos estáticos: caché primero y se actualiza en segundo plano.
  evento.respondWith(
    caches.match(peticion).then((guardado) => {
      const red = fetch(peticion).then((respuesta) => {
        if (respuesta.ok) {
          const copia = respuesta.clone();
          caches.open(CACHE).then((c) => c.put(peticion, copia));
        }
        return respuesta;
      });
      return guardado || red;
    })
  );
});
