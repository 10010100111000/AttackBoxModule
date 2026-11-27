import { triggerXSSQueue } from '../queue.js';
import { broadcastMessage } from '../routes/websocket.js';
import crypto from 'crypto';
import Redis from 'ioredis';

const redis = new Redis();

async function submitViolation(violation) {
  violation.time = new Date().toISOString();
  await redis.rpush('violation_history', JSON.stringify(violation));
  await redis.set('last_violation', JSON.stringify(violation));

  const violations = await getViolationHistory();
  broadcastMessage('update_violations', violations);
}

async function getViolationHistory() {
  const history = await redis.lrange('violation_history', 0, -1);
  return history.map(item => JSON.parse(item));
}

async function getLogs() {
  const logs = await redis.lrange('request_logs', 0, -1);
  return logs.map(log => JSON.parse(log));
}

async function handleCallback(req) {
  const logEntry = {
    method: req.method,
    headers: req.headers,
    args: req.query,
    data: req.body,
    time: new Date().toISOString()
  };

  await redis.rpush('request_logs', JSON.stringify(logEntry));
  broadcastMessage('update_logs', await getLogs());
  return { status: 'received' };
}

async function triggerXSS(payload) {
  if (typeof payload !== 'string' || payload.length === 0 || payload.length > 16384) {
    throw new Error('XSS payload must be a non-empty string of at most 16 KiB');
  }

  const job = await triggerXSSQueue.add({ xssPayload: payload });
  await redis.set(`xss_payload:${job.id}`, payload, 'EX', 300);
  return { status: 'queued', job_id: job.id };
}

async function getXSSPayload(jobId) {
  if (typeof jobId !== 'string' || !/^[0-9]+$/.test(jobId)) return '';
  return (await redis.get(`xss_payload:${jobId}`)) || '';
}

export async function fetchDefaultCSP() {
  return (await redis.get('cachedCSPHeader')) || '';
}

export async function getCachedCSP() {
  const cachedCSP = await redis.get('cachedCSPHeader');
  if (cachedCSP) {
    // Intentionally vulnerable: the same nonce is reused across responses.
    return cachedCSP;
  }

  const nonce = crypto.randomBytes(16).toString('hex');
  const cspWithNonce = `default-src 'self'; script-src 'self' 'nonce-${nonce}'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none'; report-uri /csp-report`;
  await redis.set('cachedCSPHeader', cspWithNonce);
  return cspWithNonce;
}

export {
  redis,
  handleCallback,
  submitViolation,
  getViolationHistory,
  getLogs,
  triggerXSS,
  getXSSPayload
};
