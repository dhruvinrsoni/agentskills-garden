// sw.js — service worker for the Agent Skills Garden PWA.
// Its main job is to provide a `fetch` handler — which (with the PNG icons in
// the manifest) is what lets the site install as a real app, not a bookmark.
// It also gives basic offline support via runtime caching. No hardcoded
// precache list, so it works regardless of the deploy base path.
const CACHE = 'garden-v1';

self.addEventListener('install', (e) => { self.skipWaiting(); });

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== self.location.origin) return; // let cross-origin pass through
  if (req.mode === 'navigate') {
    // network-first for pages; fall back to a cached copy offline
    e.respondWith(fetch(req).catch(() => caches.match(req)));
    return;
  }
  // cache-first for same-origin static assets
  e.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const res = await fetch(req);
      const cache = await caches.open(CACHE);
      cache.put(req, res.clone());
      return res;
    } catch (err) {
      return cached || Response.error();
    }
  })());
});
