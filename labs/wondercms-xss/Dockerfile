# Real WonderCMS 3.4.2; upstream source is never patched or replaced.
# Upstream license: MIT (retained at /srv/wcms/LICENSE-WonderCMS).
FROM alpine:3.20 AS upstream
RUN apk add --no-cache git ca-certificates \
 && git init /src \
 && git -C /src remote add origin https://github.com/WonderCMS/wondercms.git \
 && git -C /src fetch --depth=1 origin refs/tags/3.4.2 \
 && git -C /src checkout --detach FETCH_HEAD \
 && test "$(git -C /src rev-parse HEAD)" = "65ad81405af2d27f75190805ed6c1d954d6fc72b"

FROM php:8.2-alpine AS runtime
RUN set -eux; \
    apk add --no-cache curl libzip oniguruma; \
    apk add --no-cache --virtual .php-build-deps $PHPIZE_DEPS libzip-dev curl-dev oniguruma-dev; \
    docker-php-ext-install -j2 curl mbstring zip; \
    apk del .php-build-deps; \
    php -r 'foreach (["curl", "mbstring", "zip"] as $ext) {if (!extension_loaded($ext)) {exit(1);}}'
WORKDIR /srv/wcms
COPY --from=upstream /src/index.php /srv/wcms/index.php
COPY --from=upstream /src/themes /srv/wcms/themes
COPY --from=upstream /src/.htaccess /srv/wcms/.htaccess
COPY --from=upstream /src/license /srv/wcms/LICENSE-WonderCMS
COPY --from=upstream /src/version /srv/wcms/version
COPY site/router.php site/review-proof.php /srv/wcms/
COPY scripts/seed.php /usr/local/bin/wcms-seed.php
COPY scripts/start.sh /usr/local/bin/wcms-start
COPY scripts/health.php /usr/local/bin/wcms-health.php
RUN set -eux; \
    mkdir -p /srv/wcms/data/files /srv/wcms/plugins /run/wcms; \
    chown -R www-data:www-data /srv/wcms/data /srv/wcms/themes /srv/wcms/plugins /run/wcms; \
    chmod 0755 /usr/local/bin/wcms-start; \
    php -l /srv/wcms/index.php; \
    php -l /srv/wcms/router.php; \
    php -l /usr/local/bin/wcms-seed.php
USER www-data
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=4s --start-period=10s --retries=3 \
    CMD ["php", "/usr/local/bin/wcms-health.php"]
ENTRYPOINT ["/usr/local/bin/wcms-start"]
