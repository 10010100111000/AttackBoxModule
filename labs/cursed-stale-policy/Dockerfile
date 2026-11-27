# Build the real Vite frontend separately from the Node runtime.
FROM node:22-slim AS frontend-builder
WORKDIR /build

COPY challenge/frontend/package.json ./
RUN set -e; for attempt in 1 2 3; do yarn install --network-timeout 600000 --network-concurrency 1 && break || { if [ "$attempt" -eq 3 ]; then exit 1; fi; sleep 5; }; done

COPY challenge/frontend ./
RUN yarn build

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
RUN set -e; for attempt in 1 2 3; do yarn install --production --network-timeout 600000 --network-concurrency 1 && break || { if [ "$attempt" -eq 3 ]; then exit 1; fi; sleep 5; }; done && yarn cache clean

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
