# syntax=docker/dockerfile:1.7
# HTB Validation reconstruction: real second-order MariaDB injection.
# Deliberately vulnerable; deploy ONLY to private, per-user lab networks.
FROM alpine:3.20 AS runtime
RUN apk add --no-cache \
      apache2 apache2-proxy php83 php83-fpm php83-mysqli \
      mariadb mariadb-client openssh-server shadow openssl \
      curl bash util-linux util-linux-login util-linux-misc \
 && adduser -D -u 1000 -h /home/htb -s /bin/ash htb \
 && chmod 0755 /home/htb \
 && mkdir -p /var/www/html /run/apache2 /run/php /run/mysqld /run/sshd \
             /etc/php83/php-fpm.d \
 && rm -f /etc/php83/php-fpm.d/www.conf \
 && sed -i -e 's/^#LoadModule proxy_module /LoadModule proxy_module /' \
           -e 's/^#LoadModule proxy_fcgi_module /LoadModule proxy_fcgi_module /' \
           -e 's/^#ServerName .*/ServerName localhost/' /etc/apache2/httpd.conf
COPY config/apache.conf /etc/apache2/conf.d/validation.conf
COPY config/php-fpm.conf /etc/php83/php-fpm.d/validation.conf
COPY config/mariadb.cnf /etc/my.cnf.d/validation.cnf
COPY config/sshd_config /etc/ssh/sshd_config
COPY site/ /var/www/html/
COPY scripts/entrypoint.sh /usr/local/bin/validation-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/validation-healthcheck
RUN set -eu; \
    chmod 0755 /usr/local/bin/validation-entrypoint /usr/local/bin/validation-healthcheck; \
    chown root:mysql /var/www/html; \
    chmod 0775 /var/www/html; \
    chmod 0644 /var/www/html/index.php /var/www/html/account.php /var/www/html/style.css; \
    chown -R mysql:mysql /var/lib/mysql /run/mysqld; \
    php83 -l /var/www/html/index.php; \
    php83 -l /var/www/html/account.php; \
    php83 -r 'if (!class_exists("mysqli")) exit(1);'; \
    command -v su; \
    command -v script; \
    test -u "$(command -v su)"; \
    httpd -t; \
    httpd -M 2>/dev/null | grep -Fq 'proxy_module'; \
    httpd -M 2>/dev/null | grep -Fq 'proxy_fcgi_module'

EXPOSE 80 22
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=15s --timeout=8s --start-period=45s --retries=4 \
  CMD ["/usr/local/bin/validation-healthcheck"]
ENTRYPOINT ["/usr/local/bin/validation-entrypoint"]
