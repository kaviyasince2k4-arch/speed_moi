/**
 * SPEED MOI - Server Bridge for AI Studio Preview Environment
 * 
 * Automatically spawns the Python Flask application on port 5000
 * and proxies incoming HTTP requests from port 3000 to Flask.
 * On local Windows systems, users can simply run `python app.py` directly!
 */

import express, { Request, Response } from 'express';
import http from 'http';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

const app = express();
const PORT = 3000;
const FLASK_PORT = 5000;

let flaskProcess: ChildProcess | null = null;
let isFlaskReady = false;

function startFlask() {
  console.log('[SPEED MOI] Spawning Python Flask app on port 5000...');
  flaskProcess = spawn('python3', ['app.py'], {
    cwd: path.resolve('.'),
    env: { ...process.env, PORT: String(FLASK_PORT), PYTHONUNBUFFERED: '1' },
    stdio: 'inherit'
  });

  flaskProcess.on('error', (err) => {
    console.error('[SPEED MOI] Failed to start Flask process:', err);
  });

  flaskProcess.on('exit', (code, signal) => {
    console.log(`[SPEED MOI] Flask exited with code ${code}, signal ${signal}`);
    isFlaskReady = false;
  });

  // Check health periodically until ready
  const checkInterval = setInterval(() => {
    const testReq = http.request(
      {
        host: '127.0.0.1',
        port: FLASK_PORT,
        path: '/login',
        method: 'GET',
        timeout: 1000
      },
      (res) => {
        isFlaskReady = true;
        clearInterval(checkInterval);
        console.log('[SPEED MOI] Flask server is ready and accepting requests!');
      }
    );

    testReq.on('error', () => {
      // Still waiting
    });
    testReq.end();
  }, 500);
}

// Start Flask process
startFlask();

// Proxy middleware to forward all requests from port 3000 to port 5000
app.use((req: Request, res: Response) => {
  if (!isFlaskReady) {
    // Show a clean loading screen for the first 1-2 seconds while Flask starts
    res.setHeader('Content-Type', 'text/html');
    res.setHeader('Refresh', '1');
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>SPEED MOI - Starting Server</title>
        <style>
          body { font-family: system-ui, sans-serif; background: #FAF7F2; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; color: #58111A; text-align: center; }
          .box { background: white; padding: 2rem 3rem; border-radius: 12px; border-top: 4px solid #D4AF37; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
          .spinner { width: 36px; height: 36px; border: 3px solid #FAF7F2; border-top: 3px solid #D4AF37; border-radius: 50%; animation: spin 1s linear infinite; margin: 1rem auto; }
          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
      </head>
      <body>
        <div class="box">
          <h2 style="margin: 0; font-size: 1.5rem; letter-spacing: 0.05em;">SPEED MOI</h2>
          <div class="spinner"></div>
          <p style="margin: 0.5rem 0 0; color: #6B6163; font-size: 0.9rem;">Starting Python Flask server...</p>
        </div>
      </body>
      </html>
    `);
    return;
  }

  const options: http.RequestOptions = {
    host: '127.0.0.1',
    port: FLASK_PORT,
    path: req.originalUrl || req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: `127.0.0.1:${FLASK_PORT}`
    }
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    console.error('[SPEED MOI] Proxy error:', err);
    if (!res.headersSent) {
      res.status(502).send('Error connecting to Flask backend. Please reload in a moment.');
    }
  });

  req.pipe(proxyReq, { end: true });
});

process.on('SIGTERM', () => {
  if (flaskProcess) flaskProcess.kill();
  process.exit(0);
});

process.on('SIGINT', () => {
  if (flaskProcess) flaskProcess.kill();
  process.exit(0);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[SPEED MOI] Proxy server listening on port ${PORT}`);
});
