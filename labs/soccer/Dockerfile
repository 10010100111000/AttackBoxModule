# syntax=docker/dockerfile:1.7
# Reproducible upstream Tiny File Manager v2.4.3; no mock file manager.
FROM alpine:3.20 AS upstream
RUN apk add --no-cache git ca-certificates \
 && git init /source && git -C /source remote add origin https://github.com/prasathmani/tinyfilemanager.git \
 && git -C /source fetch --depth=1 origin 1dbe7c5339ad955fcb08d01d256f591a3c83d713 \
 && git -C /source checkout --detach FETCH_HEAD \
 && grep -F "define('VERSION', '2.4.3')" /source/tinyfilemanager.php

FROM node:20-bookworm-slim AS node-deps
WORKDIR /opt/soccer
COPY app/package.json ./package.json
RUN npm install --omit=dev --no-audit --no-fund && npm cache clean --force

FROM debian:bookworm-slim AS runtime
ENV DEBIAN_FRONTEND=noninteractive SOCCER_USER_FLAG="" NODE_ENV=production
RUN set -eux; \
 apt-get update; \
 apt-get install -y --no-install-recommends nginx php8.2-fpm php8.2-cli php8.2-mbstring php8.2-zip mariadb-server ca-certificates curl tini libatomic1; \
 rm -rf /var/lib/apt/lists/* /var/cache/apt/* /usr/share/doc/* /usr/share/man/*; \
 mkdir -p /var/www/html/tiny/uploads /opt/soccer /run/mysqld /run/php /data/mysql /home/player; \
 groupadd -g 10001 soccerapp; useradd -u 10001 -g 10001 -M -s /usr/sbin/nologin soccerapp; \
 chown mysql:mysql /run/mysqld /data/mysql; \
 chown www-data:www-data /var/www/html/tiny/uploads /home/player; \
 sed -i 's/^listen = .*/listen = 127.0.0.1:9000/' /etc/php/8.2/fpm/pool.d/www.conf
COPY --from=node-deps /usr/local/bin/node /usr/local/bin/node
COPY --from=node-deps /opt/soccer/node_modules /opt/soccer/node_modules
COPY --from=upstream /source/tinyfilemanager.php /var/www/html/tiny/index.php
COPY site/ /var/www/html/
COPY scripts/nginx.conf /etc/nginx/conf.d/soccer.conf
COPY scripts/filemanager-config.php /var/www/html/tiny/config.php
RUN rm -f /etc/nginx/sites-enabled/default
COPY app/server.js /opt/soccer/server.js
COPY db/init.sql /opt/soccer/init.sql
COPY scripts/start.sh /usr/local/bin/soccer-start
COPY scripts/healthcheck.sh /usr/local/bin/soccer-healthcheck
COPY flags/user.txt /home/player/user.txt
RUN set -eux; \
 chmod 0755 /usr/local/bin/soccer-start /usr/local/bin/soccer-healthcheck; \
 chmod 0400 /home/player/user.txt; \
 chown root:root /home/player/user.txt; \
 chown -R root:root /var/www/html; \
 chown www-data:www-data /var/www/html/tiny/uploads; \
 chmod 0775 /var/www/html/tiny/uploads; \
 chmod -R a+rX /var/www/html; \
 chown -R root:root /opt/soccer; \
 chown soccerapp:soccerapp /opt/soccer/server.js; \
 chmod 0400 /opt/soccer/server.js
WORKDIR /opt/soccer
EXPOSE 8080 9091
HEALTHCHECK --interval=20s --timeout=5s --start-period=60s --retries=4 CMD ["/usr/local/bin/soccer-healthcheck"]
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/soccer-start"]
