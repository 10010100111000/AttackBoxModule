# syntax=docker/dockerfile:1.7
# Bashed: real Arrexel/phpbash web shell + sudo user pivot + root cron script.
FROM alpine:3.20 AS phpbash-source
RUN apk add --no-cache ca-certificates curl git
RUN set -eux; \
    curl -fL --retry 4 https://raw.githubusercontent.com/Arrexel/phpbash/master/phpbash.php -o /tmp/phpbash.php; \
    curl -fL --retry 4 https://raw.githubusercontent.com/Arrexel/phpbash/master/LICENSE -o /tmp/LICENSE; \
    test "$(git hash-object /tmp/phpbash.php)" = "dd7ff714ad62ddcf2a06a7a44af9c342b7d83552"; \
    grep -Fq "shell_exec" /tmp/phpbash.php; \
    grep -Fq "Apache License" /tmp/LICENSE

FROM ubuntu:18.04 AS runtime
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      apache2 php7.2 libapache2-mod-php7.2 cron sudo python3 ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=phpbash-source /tmp/phpbash.php /var/www/html/dev/phpbash.php
COPY --from=phpbash-source /tmp/LICENSE /usr/share/doc/phpbash/LICENSE
COPY site/index.html /var/www/html/index.html
COPY scripts/test.py /scripts/test.py
COPY scripts/test.txt /scripts/test.txt
COPY config/root-scripts /etc/cron.d/root-scripts
COPY scripts/entrypoint.sh /usr/local/bin/bashed-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/bashed-healthcheck
COPY flags/user.txt /home/arrexel/user.txt
COPY flags/root.txt /root/root.txt
RUN set -eux; \
    useradd -m -s /bin/bash arrexel; \
    useradd -m -s /bin/bash scriptmanager; \
    mkdir -p /var/www/html/dev /scripts; \
    chown -R root:root /var/www/html; \
    chmod 0755 /var/www/html/dev; \
    chown -R scriptmanager:scriptmanager /scripts; \
    chmod 0774 /scripts; \
    chown scriptmanager:scriptmanager /scripts/test.py; \
    chmod 0644 /scripts/test.py; \
    chown root:root /scripts/test.txt; \
    chmod 0644 /scripts/test.txt; \
    chmod 0644 /etc/cron.d/root-scripts; \
    printf '%s\n' 'www-data ALL=(scriptmanager) NOPASSWD: ALL' > /etc/sudoers.d/www-data-scriptmanager; \
    chmod 0440 /etc/sudoers.d/www-data-scriptmanager; \
    chown arrexel:arrexel /home/arrexel/user.txt; \
    chmod 0644 /home/arrexel/user.txt; \
    chown root:root /root/root.txt; \
    chmod 0600 /root/root.txt; \
    chmod 0755 /usr/local/bin/bashed-entrypoint /usr/local/bin/bashed-healthcheck; \
    php -l /var/www/html/dev/phpbash.php; \
    visudo -cf /etc/sudoers; \
    apache2ctl configtest
EXPOSE 80
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=20s --timeout=6s --start-period=20s --retries=3 \
  CMD ["/usr/local/bin/bashed-healthcheck"]
ENTRYPOINT ["/usr/local/bin/bashed-entrypoint"]
