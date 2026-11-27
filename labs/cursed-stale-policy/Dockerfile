# Build the real Vite frontend separately from the Node runtime.
FROM node:22-slim AS frontend-builder
WORKDIR /build

COPY challenge/frontend/package.json ./
RUN npm config set registry https://registry.npmjs.org/ \
 && npm install --legacy-peer-deps --no-audit --no-fund --fetch-retries=5 --fetch-timeout=600000

COPY challenge/frontend ./
RUN npm run build

# Resolve backend dependencies in a disposable stage. Some upstream dependencies
# are Git-based/native, so git and the toolchain must not leak into the runtime.
FROM node:22-slim AS backend-deps
WORKDIR /app/backend
RUN apt-get update \
 && apt-get install -y --no-install-recommends git python3 make g++ \
 && rm -rf /var/lib/apt/lists/*
COPY challenge/backend/package.json ./
RUN npm config set registry https://registry.npmjs.org/ \
 && npm install --omit=dev --legacy-peer-deps --no-audit --no-fund --fetch-retries=5 --fetch-timeout=600000 \
 && npm cache clean --force

FROM node:22-slim AS runtime
ENV NODE_ENV=production \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium redis-server supervisor \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /root/.cache

WORKDIR /app/backend
COPY challenge/backend/package.json ./
COPY --from=backend-deps /app/backend/node_modules ./node_modules
COPY challenge/backend ./
COPY --from=frontend-builder /app/backend/static/dist ./static/dist
COPY config/supervisord.conf /etc/supervisord.conf
COPY flag.txt /flag.txt
COPY scripts/start.sh /usr/local/bin/cursed-start

RUN chmod 0755 /usr/local/bin/cursed-start \
 && chmod 0444 /flag.txt \
 && node --check app.js \
 && node --check queue.js \
 && node --check workers/worker.js \
 && node --check routes/xss.js \
 && node --check utils/redis.js \
 && test -s static/dist/.vite/manifest.json

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=4s --start-period=30s --retries=5 \
  CMD node -e "fetch('http://127.0.0.1:8000/').then(r => r.ok ? process.exit(0) : process.exit(1)).catch(() => process.exit(1))"

ENTRYPOINT ["/usr/local/bin/cursed-start"]
