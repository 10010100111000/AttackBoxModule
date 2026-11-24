# syntax=docker/dockerfile:1.7
# Validate PHP source in a disposable stage; the runtime receives no build tooling.
FROM alpine:3.22 AS web-build
RUN apk add --no-cache php84 php84-mysqli php84-session
WORKDIR /build
COPY site/ ./site/
RUN find site -type f -name '*.php' -print0 | xargs -0 -r -n1 php84 -l

FROM alpine:3.22 AS runtime
RUN apk add --no-cache \
      bash bind bind-openrc openrc \
      nginx php84-fpm php84-mysqli php84-session \
      mariadb mariadb-client \
      openssh-server sudo \
      fail2ban fail2ban-openrc iptables iproute2 \
      shadow openssl curl \
    && rm -f /etc/nginx/http.d/default.conf \\
    && addgroup -S security \
    && adduser -D -u 1001 -h /home/michael -s /bin/bash michael \
    && addgroup michael security \
    && mkdir -p /var/www/default /var/www/payroll /var/www/market \
       /run/named /run/php-fpm /run/mysqld /run/sshd /var/empty \
       /var/log /var/bind \
    && rm -f /etc/php84/php-fpm.d/www.conf

COPY --from=web-build /build/site/default/ /var/www/default/
COPY --from=web-build /build/site/payroll/ /var/www/payroll/
COPY --from=web-build /build/site/market/ /var/www/market/
COPY config/named.conf /etc/bind/named.conf
COPY config/trick.htb.zone /var/bind/trick.htb.zone
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/trick.conf /etc/nginx/http.d/trick.conf
COPY config/mysql.cnf /etc/my.cnf.d/trick.cnf
COPY config/php-pool-payroll.conf /etc/php84/php-fpm.d/payroll.conf
COPY config/php-pool-marketing.conf /etc/php84/php-fpm.d/marketing.conf
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/jail.local /etc/fail2ban/jail.local
COPY config/sudoers-michael /etc/sudoers.d/michael
COPY scripts/entrypoint.sh /usr/local/bin/trick-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/trick-healthcheck

RUN set -eu; \
    chown -R root:root /var/www; \
    find /var/www -type d -exec chmod 0755 {} \;; \
    find /var/www -type f -exec chmod 0644 {} \;; \
    chmod 0755 /usr/local/bin/trick-entrypoint /usr/local/bin/trick-healthcheck; \
    chmod 0440 /etc/sudoers.d/michael; \
    chown root:security /etc/fail2ban/action.d; \
    chmod 0770 /etc/fail2ban/action.d; \
    chown root:root /etc/fail2ban/action.d/iptables-multiport.conf; \
    chmod 0644 /etc/fail2ban/action.d/iptables-multiport.conf; \
    chown named:named /var/bind /var/bind/trick.htb.zone /run/named; \
    chown mysql:mysql /run/mysqld /var/lib/mysql; \
    visudo -cf /etc/sudoers; \
    php-fpm84 -t; \
    nginx -t; \
    named-checkconf /etc/bind/named.conf; \
    named-checkzone trick.htb /var/bind/trick.htb.zone

EXPOSE 22/tcp 53/tcp 53/udp 80/tcp
HEALTHCHECK --interval=15s --timeout=8s --start-period=90s --retries=4 \
  CMD ["/usr/local/bin/trick-healthcheck"]
ENTRYPOINT ["/usr/local/bin/trick-entrypoint"]
