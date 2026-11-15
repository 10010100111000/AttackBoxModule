# ==========================================
# Stage 1: Build frontend assets
# ==========================================
FROM node:22-slim AS frontend-builder

WORKDIR /build

COPY challenge/frontend/package.json ./
RUN yarn install --frozen-lockfile 2>/dev/null || yarn install

COPY challenge/frontend ./
RUN yarn build

# ==========================================
# Stage 2: Production runner
# ==========================================
FROM node:22-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    chromium \
    redis-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure Puppeteer to use the pre-installed system Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    NODE_ENV=production

# Place flag
COPY flag.txt /flag.txt
RUN chmod 0444 /flag.txt

WORKDIR /app/backend

# Copy backend dependencies definition first for layer caching
COPY challenge/backend/package.json ./
RUN yarn install --production --frozen-lockfile 2>/dev/null || yarn install --production \
    && yarn cache clean

# Copy backend source code
COPY challenge/backend ./

# Copy compiled frontend distribution from builder stage
COPY --from=frontend-builder /app/backend/static/dist ./static/dist

# Copy supervisord configuration
COPY config/supervisord.conf /etc/supervisord.conf

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=3s --retries=3 --start-period=5s \
  CMD node -e "fetch('http://127.0.0.1:8000/').then(r => r.ok ? process.exit(0) : process.exit(1)).catch(() => process.exit(1))"

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
