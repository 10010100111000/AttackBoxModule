# syntax=docker/dockerfile:1.7
# Official MongoDB server binary is extracted in a disposable Debian stage.
FROM debian:bookworm-slim AS mongo-package
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
    curl -fsSL https://pgp.mongodb.com/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg; \
    echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main' > /etc/apt/sources.list.d/mongodb-org-8.0.list; \
    apt-get update; \
    cd /tmp; \
    apt-get download mongodb-org-server; \
    dpkg-deb -x mongodb-org-server_*.deb /mongodb; \
    test -x /mongodb/usr/bin/mongod

FROM node:20-bookworm-slim AS node-deps
WORKDIR /opt/blog
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 make g++ pkg-config libxml2-dev \
    && rm -rf /var/lib/apt/lists/*
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund && npm cache clean --force

FROM node:20-bookworm-slim AS runtime
ENV NODE_ENV=production \
    MONGO_URL=mongodb://127.0.0.1:27017/blog \
    PORT=5000
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates tini libcurl4 libgssapi-krb5-2 liblzma5 libssl3 \
      libldap-2.5-0 libsasl2-2 libsnappy1v5 libzstd1 libxml2 libstdc++6; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*; \
    groupadd -g 10001 nodeblog; \
    useradd -u 10001 -g 10001 -m -s /usr/sbin/nologin nodeblog; \
    mkdir -p /opt/blog/challenge-data /run/nodeblog /data/mongo; \
    chown -R nodeblog:nodeblog /opt/blog /data /home/nodeblog
COPY --from=mongo-package /mongodb/usr/bin/mongod /usr/local/bin/mongod
COPY --from=node-deps /opt/blog/node_modules /opt/blog/node_modules
COPY package.json server.js seed.js healthcheck.js /opt/blog/
COPY models/ /opt/blog/models/
COPY routes/ /opt/blog/routes/
COPY views/ /opt/blog/views/
COPY public/ /opt/blog/public/
COPY flags/flag01.txt /run/nodeblog/flag01.txt
COPY flags/flag02.txt /opt/blog/challenge-data/xxe-flag.txt
COPY flags/user.txt /home/nodeblog/user.txt
COPY scripts/entrypoint.sh /usr/local/bin/nodeblog-entrypoint
RUN set -eux; \
    chmod 755 /usr/local/bin/nodeblog-entrypoint /usr/local/bin/mongod; \
    chown nodeblog:nodeblog /home/nodeblog/user.txt /run/nodeblog /run/nodeblog/flag01.txt /opt/blog/challenge-data/xxe-flag.txt; \
    chmod 0600 /home/nodeblog/user.txt; \
    chmod 0400 /run/nodeblog/flag01.txt /opt/blog/challenge-data/xxe-flag.txt; \
    if ldd /usr/local/bin/mongod | grep -q 'not found'; then exit 1; fi
WORKDIR /opt/blog
USER nodeblog
EXPOSE 5000
HEALTHCHECK --interval=20s --timeout=5s --start-period=45s --retries=5 \
  CMD ["node", "/opt/blog/healthcheck.js"]
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/nodeblog-entrypoint"]
