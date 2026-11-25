# syntax=docker/dockerfile:1.7
FROM alpine:3.16 AS source
RUN apk add --no-cache git
WORKDIR /src
RUN git init \
 && git remote add origin https://github.com/ImpressCMS/impresscms.git \
 && git fetch --depth 1 origin 56caca0356646ad29497ce877589326a4a76123b \
 && git checkout --detach FETCH_HEAD
RUN mkdir -p /out && cp -a /src/htdocs/. /out/
WORKDIR /content
RUN git init \
 && git remote add origin https://github.com/IPFModules/content.git \
 && git fetch --depth 1 origin 1a6395e6d5f85f39ee241987bc0de89a1dc9117e \
 && git checkout --detach FETCH_HEAD
RUN mkdir -p /out/modules/content && cp -a /content/. /out/modules/content/

FROM php:7.4-fpm-alpine3.16 AS runtime
RUN apk add --no-cache curl iproute2 mariadb mariadb-client nginx supervisor \
 && apk add --no-cache --virtual .php-build-deps \
      $PHPIZE_DEPS curl-dev freetype-dev icu-dev libjpeg-turbo-dev \
      libpng-dev libxml2-dev libzip-dev oniguruma-dev zlib-dev \
 && docker-php-ext-configure gd --with-freetype --with-jpeg \
 && docker-php-ext-install -j"$(nproc)" curl dom exif gd intl mbstring mysqli opcache pdo_mysql simplexml xml xmlreader xmlwriter zip \
 && apk del .php-build-deps \
 && mkdir -p /run/mysqld /run/nginx /var/www/trust /var/www/html/uploads /var/www/html/cache /var/www/html/templates_c /var/lib/mysql \
 && chown -R mysql:mysql /run/mysqld /var/lib/mysql \
 && chown -R www-data:www-data /var/www/trust /var/www/html/uploads /var/www/html/cache /var/www/html/templates_c
COPY --from=source /out/ /var/www/html/
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/supervisord.conf /etc/supervisord.conf
COPY config/php.ini /usr/local/etc/php/conf.d/zz-impresscms.ini
COPY scripts/entrypoint.sh /usr/local/bin/impresscms-entrypoint
COPY scripts/install-cms.sh /usr/local/bin/impresscms-install
COPY scripts/healthcheck.sh /usr/local/bin/impresscms-healthcheck
COPY scripts/db-health.php /usr/local/bin/impresscms-db-health.php
RUN chmod 0755 /usr/local/bin/impresscms-entrypoint /usr/local/bin/impresscms-install /usr/local/bin/impresscms-healthcheck \
 && chown -R root:root /var/www/html \
 && chmod -R a+rX /var/www/html
EXPOSE 80
HEALTHCHECK --interval=20s --timeout=5s --start-period=90s --retries=3 CMD ["/usr/local/bin/impresscms-healthcheck"]
ENTRYPOINT ["/usr/local/bin/impresscms-entrypoint"]
