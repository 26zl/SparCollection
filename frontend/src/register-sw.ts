export function registerSW(): void {
  if (!import.meta.env.PROD) {
    return;
  }
  if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch((err) => {
        console.warn('SW register failed:', err);
      });
    });
  }
}
