import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon',
};

export function startCompanionServer(appDir, options = {}) {
  const host = '127.0.0.1';
  const port = options.port || 4173;
  const resolvedRoot = path.resolve(appDir);

  if (!fs.existsSync(resolvedRoot)) {
    throw new Error(`Companion application directory not found: ${resolvedRoot}`);
  }

  const server = http.createServer((req, res) => {
    // Only allow GET / HEAD
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405, { 'Content-Type': 'text/plain' });
      res.end('Method Not Allowed');
      return;
    }

    const parsedUrl = new URL(req.url, `http://${host}:${port}`);
    let reqPath = decodeURIComponent(parsedUrl.pathname);
    if (reqPath === '/' || reqPath === '') {
      reqPath = '/index.html';
    }

    const fullPath = path.resolve(resolvedRoot, '.' + reqPath);

    // Prevent path traversal outside resolvedRoot
    if (!fullPath.startsWith(resolvedRoot + path.sep) && fullPath !== resolvedRoot) {
      res.writeHead(403, { 'Content-Type': 'text/plain' });
      res.end('Forbidden: Access outside application root is prohibited');
      return;
    }

    if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not Found');
      return;
    }

    const ext = path.extname(fullPath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': 'no-cache',
      'X-Content-Type-Options': 'nosniff',
    });

    if (req.method === 'HEAD') {
      res.end();
      return;
    }

    const stream = fs.createReadStream(fullPath);
    stream.pipe(res);
  });

  return new Promise((resolve, reject) => {
    server.on('error', (err) => {
      reject(err);
    });
    server.listen(port, host, () => {
      const url = `http://${host}:${port}/`;
      resolve({
        server,
        url,
        close: () => new Promise((res) => server.close(res)),
      });
    });
  });
}
