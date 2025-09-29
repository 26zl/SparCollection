// Simple network-first SW – ignore API calls
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

  // Don't intercept API calls—let browser go directly to Azure Functions
  try {
    const url = new URL(event.request.url);
    if (url.pathname.startsWith('/api/')) {
      return;
    }
  } catch (_) {
    // ignore URL parsing errors
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => response)
      .catch(() => new Response('Offline', { status: 503, statusText: 'Offline' })),
  );
});
