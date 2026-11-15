# syntax=docker/dockerfile:1.7
# Download and unpack upstream artifacts in a disposable stage.
FROM ubuntu:22.04 AS artifacts
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl tar; \
    rm -rf /var/lib/apt/lists/*

ARG APPORT_VERSION=2.20.11-0ubuntu82
ARG APPORT_ARCHIVE=https://archive.ubuntu.com/ubuntu/pool/main/a/apport
ARG JOOMLA_URL="https://downloads.joomla.org/cms/joomla4/4-2-6/Joomla_4.2.6-Stable-Full_Package.tar.gz?format=gz"
RUN set -eux; \
    mkdir -p /opt/artifacts/debs /opt/artifacts/joomla; \
    for pkg in apport python3-apport python3-problem-report; do \
        curl --fail --location --retry 3 \
            --output "/opt/artifacts/debs/${pkg}.deb" \
            "${APPORT_ARCHIVE}/${pkg}_${APPORT_VERSION}_all.deb"; \
        test "$(dpkg-deb -f "/opt/artifacts/debs/${pkg}.deb" Version)" = "$APPORT_VERSION"; \
        test "$(dpkg-deb -f "/opt/artifacts/debs/${pkg}.deb" Package)" = "$pkg"; \
    done; \
    curl --fail --location --retry 3 --output /tmp/joomla.tar.gz "$JOOMLA_URL"; \
    echo 'e01705da3de1a541d2b3c07791968e01  /tmp/joomla.tar.gz' | md5sum -c -; \
    tar -xzf /tmp/joomla.tar.gz -C /opt/artifacts/joomla; \
    rm -f /tmp/joomla.tar.gz

# Runtime stays on Ubuntu 22.04: Alpine would break Debian packaging and
# the authentic vulnerable apport-cli dependency/environment assumptions.
FROM ubuntu:22.04 AS runtime
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC
ARG APPORT_VERSION=2.20.11-0ubuntu82

COPY --from=artifacts /opt/artifacts/debs/ /tmp/apport-debs/
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      nginx mariadb-server mariadb-client \
      php8.1-fpm php8.1-cli php8.1-mysql php8.1-xml php8.1-mbstring \
      php8.1-curl php8.1-zip php8.1-gd php8.1-intl \
      openssh-server sudo less procps curl \
      apport python3-apport python3-problem-report; \
    dpkg --force-downgrade -i \
      /tmp/apport-debs/python3-problem-report.deb \
      /tmp/apport-debs/python3-apport.deb \
      /tmp/apport-debs/apport.deb; \
    for pkg in apport python3-apport python3-problem-report; do \
      test "$(dpkg-query -W -f='${Version}' "$pkg")" = "$APPORT_VERSION"; \
    done; \
    test -f /usr/bin/apport-cli; \
    apt-mark hold apport python3-apport python3-problem-report; \
    rm -rf /tmp/apport-debs /var/lib/apt/lists/* /var/cache/apt/archives/*.deb \
      /var/log/apt/* /var/log/dpkg.log; \
    mkdir -p /var/www/dev.devvortex.htb /var/www/devvortex.htb /run/php /run/sshd

COPY --from=artifacts --chown=www-data:www-data /opt/artifacts/joomla/ /var/www/dev.devvortex.htb/
COPY config/nginx.conf /etc/nginx/sites-available/default
COPY site/index.html /var/www/devvortex.htb/index.html
COPY scripts/start.sh /usr/local/bin/start-lab
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
COPY tests/check-apport.sh /usr/local/bin/check-apport.sh
RUN set -eux; \
    chmod 755 /usr/local/bin/start-lab /usr/local/bin/healthcheck.sh /usr/local/bin/check-apport.sh; \
    useradd -m -s /bin/bash logan; \
    echo 'logan:tequieromucho' | chpasswd; \
    echo 'logan ALL=(root) NOPASSWD: /usr/bin/apport-cli' > /etc/sudoers.d/devvortex-lab; \
    chmod 440 /etc/sudoers.d/devvortex-lab; \
    printf 'DEVVORTEX{local_user_flag_demo}\n' > /home/logan/user.txt; \
    printf 'DEVVORTEX{local_root_flag_demo}\n' > /root/root.txt; \
    chown logan:logan /home/logan/user.txt; \
    chmod 600 /home/logan/user.txt /root/root.txt; \
    printf '\nPasswordAuthentication yes\nPermitRootLogin no\nUsePAM yes\n' >> /etc/ssh/sshd_config; \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* \
      /usr/share/lintian/* /var/cache/man/* /tmp/*

EXPOSE 80 22
HEALTHCHECK --interval=20s --timeout=8s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/healthcheck.sh"]
ENTRYPOINT ["/usr/local/bin/start-lab"]
