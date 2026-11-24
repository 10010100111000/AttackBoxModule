'use strict';
const express = require('express');
const mysql = require('mysql2/promise');
const { WebSocketServer } = require('ws');
const http = require('http');

const app = express();
app.disable('x-powered-by');
app.use(express.urlencoded({ extended: false }));
app.use(express.static('/var/www/html/player', { index: false }));
const db = mysql.createPool({ host: '127.0.0.1', user: 'ticket_reader', password: 'ticket_reader_pass', database: 'soccer_db', connectionLimit: 3 });
const users = new Map();
app.get('/healthz', async (_req, res) => {
  try { await db.query('SELECT 1'); res.send('ok'); } catch (_) { res.status(503).send('db unavailable'); }
});
app.get('/', (_req, res) => res.sendFile('/var/www/html/player/index.html'));
app.get('/check', (_req, res) => res.sendFile('/var/www/html/player/check.html'));
app.post('/register', (req, res) => {
  const { username, password } = req.body;
  if (typeof username !== 'string' || !/^[a-z0-9_]{3,20}$/i.test(username) || typeof password !== 'string' || password.length < 4) {
    return res.status(400).send('Invalid registration');
  }
  users.set(username, password);
  res.redirect('/check');
});
const httpServer = http.createServer(app);
httpServer.listen(3000, '127.0.0.1');
const wsServer = new WebSocketServer({ host: '0.0.0.0', port: 9091, maxPayload: 4096 });
wsServer.on('connection', (socket) => {
  socket.on('message', async (packet) => {
    try {
      const payload = JSON.parse(packet.toString());
      if (!payload || (typeof payload.id !== 'string' && typeof payload.id !== 'number')) return socket.send('Invalid ticket');
      // Intentional original Soccer-style vulnerability: actual SQL interpolation into MariaDB.
      const [rows] = await db.query(`SELECT id FROM tickets WHERE id = ${payload.id}`);
      socket.send(rows.length > 0 ? 'Ticket Exists' : "Ticket Doesn't Exist");
    } catch (_) { socket.send('Ticket lookup failed'); }
  });
});
process.on('SIGTERM', () => { wsServer.close(); httpServer.close(); db.end(); });
