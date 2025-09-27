// Enkel network-first SW – ignorer API-kall
self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  // Ikke kapre API-kall—la nettleseren gå direkte til Azure Functions
  try {
    const url = new URL(event.request.url);
    if (url.pathname.startsWith('/api/')) {
      return;
    }
  } catch (_) {
    // ignorer feil i URL-parsing
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => response)
      .catch(() => new Response('Offline', { status: 503, statusText: 'Offline' })),
  );
});
