// Service worker de GolStats: hace que la app sea instalable y que abra aunque no haya internet.
//  - Archivos estáticos (CSS, JS, iconos): se guardan y se actualizan en segundo plano.
//  - Páginas: primero se pide a internet (datos frescos); si no hay conexión, se muestra la última vista guardada.
const VERSION = "golstats-v1";
const PRECACHE = ["/static/css/style.css", "/static/js/main.js", "/static/icons/icon-192.png"];
const OFFLINE_HTML = `<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sin conexión</title><body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#0a0e16;color:#e8edf5;font-family:system-ui,sans-serif;text-align:center;padding:24px">
<div><h1>📡 Sin conexión</h1><p style="color:#8b98ad">No hay internet y todavía no guardaste esta pantalla.<br>Volvé a intentar cuando tengas conexión.</p>
<p><a href="/" style="color:#22e07a;font-weight:700">Reintentar</a></p></div></body></html>`;

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  if (url.origin === location.origin && url.pathname.startsWith("/static/")) {
    e.respondWith(
      caches.open(VERSION).then(async (cache) => {
        const hit = await cache.match(req);
        const net = fetch(req).then((r) => { if (r.ok) cache.put(req, r.clone()); return r; }).catch(() => hit);
        return hit || net;
      })
    );
    return;
  }

  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((r) => { if (r.ok) { const copy = r.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); } return r; })
        .catch(async () => (await caches.match(req)) ||
          new Response(OFFLINE_HTML, { status: 503, headers: { "Content-Type": "text/html; charset=utf-8" } }))
    );
  }
});
