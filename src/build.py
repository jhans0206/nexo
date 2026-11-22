# Builds the installable GitHub Pages version (web/) from nexo.html, the shared app source.
import shutil, hashlib, os
d = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(d, "nexo.html")).read()
ver = hashlib.sha1(src.encode()).hexdigest()[:8]
head = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0E6B5C">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NEXO">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="icon-192.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
tail = """
<script>if("serviceWorker" in navigator && location.protocol==="https:"){navigator.serviceWorker.register("sw.js");}</script>
</body></html>"""
w = os.path.join(d, "web")
open(os.path.join(w, "index.html"), "w").write(head + src + tail)
open(os.path.join(w, "manifest.webmanifest"), "w").write("""{
  "name": "NEXO",
  "short_name": "NEXO",
  "description": "Mi centro de control financiero personal",
  "lang": "es-PE",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#EEF2F0",
  "theme_color": "#0E6B5C",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
""")
open(os.path.join(w, "sw.js"), "w").write("""// NEXO offline cache. Version changes on every build so updates arrive.
const CACHE = "nexo-%s";
const CORE = ["./", "index.html", "manifest.webmanifest", "apple-touch-icon.png", "icon-192.png", "icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  // App page: network first (to get updates), cache when offline.
  if (e.request.mode === "navigate") {
    e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put("index.html", c)); return r; }).catch(() => caches.match("index.html")));
    return;
  }
  // Icons, fonts: cache first.
  if (url.origin === location.origin || url.host.endsWith("fonts.googleapis.com") || url.host.endsWith("fonts.gstatic.com")) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); return r; })));
  }
});
""" % ver)
for f in ["apple-touch-icon.png", "icon-192.png", "icon-512.png"]:
    shutil.copy(os.path.join(d, f), os.path.join(w, f))
open(os.path.join(w, ".nojekyll"), "w").write("")
print("built", ver)
