# Deliberately vulnerable training image. DO NOT expose it to the Internet.
FROM node:20-bookworm-slim

ENV NODE_ENV=production \
    PORT=80

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server tini \
    && mkdir -p /run/sshd /root/Backend \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/Backend
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund \
    && npm cache clean --force
COPY server.js healthcheck.js ./
COPY public/ ./public/
COPY start.sh /usr/local/bin/bike-start
COPY sshd_config /etc/ssh/sshd_config.d/10-bike-lab.conf
COPY flags/root.txt /root/flag.txt
RUN chmod 755 /usr/local/bin/bike-start && chmod 600 /root/flag.txt

EXPOSE 22 80
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
  CMD ["node", "/root/Backend/healthcheck.js"]
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/bike-start"]
