'use strict';
const express = require('express');
const handlebars = require('handlebars');
const net = require('net');
const path = require('path');

const app = express();
app.disable('x-powered-by');
app.use(express.urlencoded({ extended: false, limit: '32kb' }));
app.use('/assets', express.static(path.join(__dirname, 'public')));

function sshStatus() {
  return new Promise((resolve) => {
    const s = net.createConnection({ host: '127.0.0.1', port: 22 });
    s.setTimeout(1500);
    s.once('data', (buf) => { resolve(buf.toString('utf8').startsWith('SSH-2.0-')); s.destroy(); });
    s.once('timeout', () => { resolve(false); s.destroy(); });
    s.once('error', () => resolve(false));
    s.once('end', () => resolve(false));
  });
}

app.get('/healthz', async (_req, res) => {
  const ssh = await sshStatus();
  res.status(ssh ? 200 : 503).json({
    status: ssh ? 'ok' : 'degraded',
    services: { web: 'ok', ssh: ssh ? 'ok' : 'down' }
  });
});

// VULNERABILITY: attacker-controlled email is inserted directly into template
// SOURCE and then compiled. Handlebars 4.1.1 intentionally allows the
// constructor/process.mainModule chain illustrated in Bike.pdf.
// This is intentional for a LOCAL training lab only.
function render(email) {
  const hasEmail = email !== undefined;
  const resultHtml = hasEmail ? `<p class="result">We will contact you at: ${email}</p>` : '';
  const tpl = `<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Bike | Under Construction</title><link rel="stylesheet" href="/assets/style.css" /></head>
<body><main class="page"><div class="glow-card"><span class="rider">🚴</span></div>
<h1>Hello, there<span class="cursor">|</span></h1>
<p class="lead">WE CAN LET YOU KNOW ONCE WE ARE UP AND RUNNING.</p>
<form action="/" method="POST"><div class="fields">
<input type="text" name="email" placeholder="E-mail" aria-label="E-mail" required />
<button type="submit">SUBMIT</button></div></form>${resultHtml}
</main></body></html>`;
  return handlebars.compile(tpl)({});
}

app.get('/', (_req, res) => res.type('html').send(render()));
app.post('/', (req, res) => {
  const email = typeof req.body.email === 'string' ? req.body.email : '';
  // No email validation is intentional: the PDF submits template expressions here.
  try {
    res.type('html').send(render(email));
  } catch (error) {
    // Showing the template error is part of the original machine's behavior.
    res.status(500).type('text/plain').send(error.stack || String(error));
  }
});

const port = Number(process.env.PORT || 80);
app.listen(port, '0.0.0.0', () => console.log(`Bike lab listening on ${port}`));
