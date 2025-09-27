import express from 'express';
import compression from 'compression';
import { createProxyMiddleware } from 'http-proxy-middleware';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import rateLimit from 'express-rate-limit';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = parseInt(process.env.PORT || '8080', 10);
const distDir = path.join(__dirname, 'frontend', 'dist');

app.disable('x-powered-by');
app.use(compression());

app.get('/healthz', (_req, res) => res.status(200).send('ok'));

let target = process.env.FUNCTIONS_BASE_URL;
if (!target && process.env.NODE_ENV !== 'production') {
  target = 'http://localhost:7071';
}

if (!target) {
  console.warn('WARNING: FUNCTIONS_BASE_URL is not set. /api calls will 502.');
  app.use('/api', (_req, res) => res.status(502).send('FUNCTIONS_BASE_URL not configured'));
} else {
  app.use(
    '/api',
    createProxyMiddleware({
      target,
      changeOrigin: true,
      xfwd: true,
      logLevel: 'warn',
      pathRewrite: { '^/api': '/api' },
      onProxyReq: (proxyReq) => {
        if (!proxyReq.getHeader('content-type')) {
          proxyReq.setHeader('content-type', 'application/json');
        }
      },
    }),
  );
}

app.use(
  express.static(distDir, {
    index: false,
    maxAge: '1h',
    setHeaders: (res, filePath) => {
      if (/\.(html)$/i.test(filePath)) {
        res.setHeader('Cache-Control', 'no-store');
      }
    },
  }),
);

const catchAllLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, 
  max: 100, 
});

app.get('*', catchAllLimiter, (_req, res) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

const server = app.listen(port, '0.0.0.0', () => {
  const addr = server.address();
  const actualPort = typeof addr === 'object' && addr ? addr.port : port;
  console.log(`Web listening on http://0.0.0.0:${actualPort}`);
  if (target) console.log(`Proxying /api/* -> ${target}`);
});
