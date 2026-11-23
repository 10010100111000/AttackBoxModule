# Real WonderCMS 3.4.2 plus an instance-local admin review bot.
# The Worker starts this single target image; it does not run the bot itself.
FROM alpine:3.20 AS upstream
RUN apk add --no-cache git ca-certificates \
 && git init /src \
 && git -C /src remote add origin https://github.com/WonderCMS/wondercms.git \
 && git -C /src fetch --depth=1 origin refs/tags/3.4.2 \
 && git -C /src checkout --detach FETCH_HEAD \
 && test "$(git -C /src rev-parse HEAD)" = "65ad81405af2d27f75190805ed6c1d954d6fc72b"

FROM php:8.2-alpine AS runtime
RUN set -eux; \
    apk add --no-cache curl libzip oniguruma chromium chromium-chromedriver python3 py3-pip su-exec; \
    apk add --no-cache --virtual .php-build-deps $PHPIZE_DEPS libzip-dev curl-dev oniguruma-dev; \
    docker-php-ext-install -j2 curl mbstring zip; \
    apk del .php-build-deps; \
    php -r 'foreach (["curl", "mbstring", "zip"] as $ext) {if (!extension_loaded($ext)) {exit(1);}}'; \
    python3 -m pip install --no-cache-dir --break-system-packages --target=/opt/wcms-bot-deps selenium==4.33.0; \
    addgroup -S wcmsbot; \
    adduser -S -D -h /home/wcmsbot -G wcmsbot wcmsbot; \
    addgroup www-data wcmsbot; \
    mkdir -p /home/wcmsbot /run/wcms/reports /run/wcms/bot-state/profiles /opt/wcms-bot; \
    chown -R wcmsbot:wcmsbot /home/wcmsbot /run/wcms/bot-state; \
    chown www-data:wcmsbot /run/wcms/reports; \
    chmod 2770 /run/wcms/reports; \
    chmod 0750 /run/wcms/bot-state; chmod 0700 /run/wcms/bot-state/profiles
ENV PYTHONPATH=/opt/wcms-bot-deps HOME=/home/wcmsbot
WORKDIR /srv/wcms
COPY --from=upstream /src/index.php /srv/wcms/index.php
COPY --from=upstream /src/themes /srv/wcms/themes
COPY --from=upstream /src/.htaccess /srv/wcms/.htaccess
COPY --from=upstream /src/license /srv/wcms/LICENSE-WonderCMS
COPY --from=upstream /src/version /srv/wcms/version
COPY site/router.php site/review-proof.php site/contact.php /srv/wcms/
COPY scripts/seed.php /usr/local/bin/wcms-seed.php
COPY scripts/start.sh /usr/local/bin/wcms-start
COPY scripts/health.php /usr/local/bin/wcms-health.php
COPY bot/review_bot.py /opt/wcms-bot/review_bot.py
RUN set -eux; \
    mkdir -p /srv/wcms/data/files /srv/wcms/plugins; \
    chown -R www-data:www-data /srv/wcms/data /srv/wcms/themes /srv/wcms/plugins; \
    chmod 0755 /usr/local/bin/wcms-start; \
    php -l /srv/wcms/index.php; \
    php -l /srv/wcms/router.php; \
    php -l /srv/wcms/contact.php; \
    php -l /srv/wcms/review-proof.php; \
    php -l /usr/local/bin/wcms-seed.php; \
    python3 -m py_compile /opt/wcms-bot/review_bot.py
USER root
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=5s --start-period=35s --retries=3 \
    CMD ["php", "/usr/local/bin/wcms-health.php"]
ENTRYPOINT ["/usr/local/bin/wcms-start"]
