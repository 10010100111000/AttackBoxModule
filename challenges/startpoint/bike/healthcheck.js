'use strict';
const http = require('http');
const net = require('net');

function checkWeb() {
  return new Promise((resolve) => {
    const req = http.get({ hostname: '127.0.0.1', port: 80, path: '/healthz', timeout: 2000 }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve(res.statusCode === 200 && data.status === 'ok' && data.services.web === 'ok' && data.services.ssh === 'ok');
        } catch (_) { resolve(false); }
      });
    });
    req.on('timeout', () => req.destroy());
    req.on('error', () => resolve(false));
  });
}

function checkSsh() {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: '127.0.0.1', port: 22 });
    socket.setTimeout(2000);
    socket.once('data', (data) => { resolve(data.toString('utf8').startsWith('SSH-2.0-')); socket.destroy(); });
    socket.once('timeout', () => { resolve(false); socket.destroy(); });
    socket.once('error', () => resolve(false));
    socket.once('end', () => resolve(false));
  });
}

Promise.all([checkWeb(), checkSsh()]).then(([web, ssh]) => {
  if (!web || !ssh) {
    console.error(JSON.stringify({ web, ssh }));
    process.exitCode = 1;
  }
}).catch((err) => {
  console.error(err.message);
  process.exitCode = 1;
});
