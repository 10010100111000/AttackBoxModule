const http = require('http');

http.get('http://127.0.0.1:5000/healthz', { timeout: 3000 }, (response) => {
  let content = '';
  response.on('data', (chunk) => { content += chunk.toString(); });
  response.on('end', () => {
    try {
      const status = JSON.parse(content);
      process.exit(response.statusCode === 200 && status.web === 'ok' && status.mongodb === 'ok' ? 0 : 1);
    } catch {
      process.exit(1);
    }
  });
}).on('error', () => process.exit(1));
