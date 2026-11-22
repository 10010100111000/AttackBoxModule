# syntax=docker/dockerfile:1.7
# Reconstructed HTB Union (2021) — real MariaDB, PHP, nginx, SSH and iptables.
# The original proprietary PHP website source is not available.
FROM alpine:3.20 AS bootstrap-css
RUN apk add --no-cache ca-certificates curl \
 && curl -fLsS --retry 4 --connect-timeout 15 \
      https://cdn.jsdelivr.net/npm/bootstrap@4.1.1/dist/css/bootstrap.min.css \
      -o /tmp/bootstrap.min.css \
 && test "$(wc -c < /tmp/bootstrap.min.css)" -gt 100000

FROM alpine:3.20 AS runtime
RUN apk add --no-cache \
      bash ca-certificates curl nginx php83 php83-fpm php83-mysqli \
      mariadb mariadb-client openssh-server sudo iptables shadow openssl \
 && addgroup -S www-data \
 && adduser -D -S -G www-data -s /sbin/nologin www-data \
 && adduser -D -u 1001 -h /home/uhc -s /bin/ash uhc \
 && echo 'uhc:uhc-11qual-global-pw' | chpasswd \
 && mkdir -p /var/www/html/css /etc/sudoers.d /run/nginx /run/mysqld /run/sshd \
             /etc/my.cnf.d \
 && rm -f /etc/nginx/http.d/default.conf \
 && rm -f /etc/php83/php-fpm.d/www.conf \
 && printf '%s\n' 'www-data ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/union-www-data \
 && chmod 0440 /etc/sudoers.d/union-www-data \
 && ln -sf "$(command -v iptables)" /usr/sbin/iptables \
 && chown -R mysql:mysql /var/lib/mysql /run/mysqld
COPY --from=bootstrap-css /tmp/bootstrap.min.css /var/www/html/css/bootstrap.min.css
COPY config/nginx.conf /etc/nginx/http.d/union.conf
COPY config/php-pool.conf /etc/php83/php-fpm.d/union.conf
COPY config/mariadb-union.cnf /etc/my.cnf.d/union.cnf
COPY config/sshd_config /etc/ssh/sshd_config
COPY site/ /var/www/html/
COPY flags/user.txt /home/uhc/user.txt
COPY flags/root.txt /root/root.txt
COPY scripts/entrypoint.sh /usr/local/bin/union-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/union-healthcheck
RUN set -eu; \
    chown -R root:root /var/www/html; \
    chmod 0755 /var/www/html /var/www/html/css; \
    chmod 0644 /var/www/html/*.php /var/www/html/*.js /var/www/html/css/*.css; \
    chown uhc:uhc /home/uhc/user.txt; chmod 0640 /home/uhc/user.txt; \
    chown root:root /root/root.txt; chmod 0600 /root/root.txt; \
    chmod 0755 /usr/local/bin/union-entrypoint /usr/local/bin/union-healthcheck; \
    chmod 0600 /etc/ssh/sshd_config; \
    php83 -l /var/www/html/index.php; \
    php83 -l /var/www/html/challenge.php; \
    php83 -l /var/www/html/firewall.php; \
    nginx -t; \
    visudo -cf /etc/sudoers

EXPOSE 80 22
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=15s --timeout=7s --start-period=45s --retries=4 \
  CMD ["/usr/local/bin/union-healthcheck"]
ENTRYPOINT ["/usr/local/bin/union-entrypoint"]
