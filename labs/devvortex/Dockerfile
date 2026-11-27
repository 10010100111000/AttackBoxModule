# syntax=docker/dockerfile:1.7
FROM ubuntu:22.04 AS artifacts
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; apt-get update; apt-get install -y --no-install-recommends ca-certificates curl tar; rm -rf /var/lib/apt/lists/*
ARG JOOMLA_URL="https://downloads.joomla.org/cms/joomla4/4-2-6/Joomla_4.2.6-Stable-Full_Package.tar.gz?format=gz"
RUN set -eux; mkdir -p /opt/artifacts/joomla; curl --fail --location --retry 3 --output /tmp/joomla.tar.gz "$JOOMLA_URL"; echo 'e01705da3de1a541d2b3c07791968e01  /tmp/joomla.tar.gz' | md5sum -c -; tar -xzf /tmp/joomla.tar.gz -C /opt/artifacts/joomla; rm -f /tmp/joomla.tar.gz

FROM ubuntu:22.04 AS runtime
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC
RUN set -eux; apt-get update; apt-get install -y --no-install-recommends nginx mariadb-server mariadb-client php8.1-fpm php8.1-cli php8.1-mysql php8.1-xml php8.1-mbstring php8.1-curl php8.1-zip php8.1-gd php8.1-intl curl procps; rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb /var/log/apt/* /var/log/dpkg.log; mkdir -p /var/www/dev.devvortex.htb /var/www/devvortex.htb /run/php

COPY --from=artifacts --chown=www-data:www-data /opt/artifacts/joomla/ /var/www/dev.devvortex.htb/
COPY config/nginx.conf /etc/nginx/sites-available/default
COPY site/index.html /var/www/devvortex.htb/index.html
COPY flags/user.txt /tmp/devvortex-user.txt
COPY scripts/start.sh /usr/local/bin/start-lab
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN set -eux; chmod 755 /usr/local/bin/start-lab /usr/local/bin/healthcheck.sh; install -d -o www-data -g www-data -m 0750 /home/www-data; install -o www-data -g www-data -m 0400 /tmp/devvortex-user.txt /home/www-data/user.txt; rm -f /tmp/devvortex-user.txt; rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* /usr/share/lintian/* /var/cache/man/* /tmp/*

EXPOSE 80
HEALTHCHECK --interval=20s --timeout=8s --start-period=120s --retries=3 CMD ["/usr/local/bin/healthcheck.sh"]
ENTRYPOINT ["/usr/local/bin/start-lab"]
