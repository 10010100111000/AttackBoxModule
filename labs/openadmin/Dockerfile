# syntax=docker/dockerfile:1.7
# OpenAdmin: authentic OpenNetAdmin v18.1.1 + MySQL + SSH + internal PHP app.
FROM alpine:3.20 AS ona-source
RUN apk add --no-cache ca-certificates curl tar
RUN set -eux; \
    curl -fL --retry 4 --connect-timeout 20 \
      "https://codeload.github.com/opennetadmin/ona/tar.gz/refs/tags/v18.1.1" \
      -o /tmp/ona.tar.gz; \
    mkdir -p /tmp/src /opt/ona; \
    tar -xzf /tmp/ona.tar.gz -C /tmp/src; \
    cp -a /tmp/src/ona-18.1.1/. /opt/ona/; \
    test "$(cat /opt/ona/VERSION)" = "v18.1.1"; \
    grep -Fq 'function ws_ping' /opt/ona/www/winc/tooltips.inc.php; \
    grep -Fq 'shell_exec' /opt/ona/www/winc/tooltips.inc.php; \
    test -s /opt/ona/docs/LICENSE

FROM ubuntu:18.04 AS runtime
ENV DEBIAN_FRONTEND=noninteractive TERM=xterm
RUN apt-get update && apt-get install -y --no-install-recommends \
      apache2 mysql-server \
      php7.2 php7.2-cli libapache2-mod-php7.2 php7.2-mysql php7.2-gmp \
      php7.2-xml php7.2-mbstring php7.2-gd php7.2-curl php7.2-zip \
      openssh-server sudo nano curl ca-certificates iproute2 net-tools \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ona-source /opt/ona /opt/ona
COPY config/ona.conf /etc/apache2/conf-available/ona.conf
COPY config/internal.conf /etc/apache2/sites-available/internal.conf
COPY config/sshd_config /etc/ssh/sshd_config
COPY internal/index.php /var/www/internal/index.php
COPY internal/main.php /var/www/internal/main.php
COPY internal/logout.php /var/www/internal/logout.php
COPY scripts/entrypoint.sh /usr/local/bin/openadmin-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/openadmin-healthcheck
COPY flags/user.txt /home/joanna/user.txt
COPY flags/root.txt /root/root.txt
RUN set -eux; \
    useradd -m -s /bin/bash jimmy; \
    useradd -m -s /bin/bash joanna; \
    echo 'jimmy:n1nj4W4rri0R!' | chpasswd; \
    echo 'joanna:unused-openadmin-password' | chpasswd; \
    mkdir -p /home/joanna/.ssh /var/www/internal /var/log; \
    ssh-keygen -q -m PEM -t rsa -b 2048 -N 'bloodninjas' -f /home/joanna/.ssh/id_rsa; \
    cp /home/joanna/.ssh/id_rsa.pub /home/joanna/.ssh/authorized_keys; \
    chown -R joanna:joanna /home/joanna/.ssh; \
    chmod 0700 /home/joanna/.ssh; \
    chmod 0600 /home/joanna/.ssh/authorized_keys; \
    chmod 0644 /home/joanna/.ssh/id_rsa; \
    chown -R www-data:www-data /var/www/internal; \
    touch /var/log/ona.log; chown www-data:www-data /var/log/ona.log; \
    mkdir -p /opt/ona/www/local/config; \
    chown -R root:www-data /opt/ona; \
    chmod -R o+rX /opt/ona; \
    chmod 0775 /opt/ona/www/local/config; \
    printf '%s\n' 'joanna ALL=(ALL) NOPASSWD: /bin/nano /opt/priv' > /etc/sudoers.d/joanna; \
    chmod 0440 /etc/sudoers.d/joanna; \
    touch /opt/priv; chmod 0644 /opt/priv; \
    printf '%s\n' 'Listen 127.0.0.1:52846' >> /etc/apache2/ports.conf; \
    a2enmod rewrite; a2enconf ona; a2ensite internal; \
    php -r 'if (hash("sha512", "Revealed") !== "00e302ccdcf1c60b8ad50ea50cf72b939705f49f40f0dc658801b4680b7d758eebdc2e9f9ba8ba3ef8a8bb9a796d34ba2e856838ee9bdde852b8ec3b3a0523b1") exit(1);'; \
    service mysql start; \
    printf '\n\n\n\n\nn1nj4W4rri0R!\n\ndefault\nopenadmin.htb\n' | php /opt/ona/install/installcli.php >/tmp/ona-install.log 2>&1; \
    test -s /opt/ona/www/local/config/database_settings.inc.php; \
    grep -Fq "n1nj4W4rri0R!" /opt/ona/www/local/config/database_settings.inc.php; \
    test -s /tmp/ona-install.log; \
    service mysql stop; \
    chown -R root:www-data /opt/ona; \
    chmod 0644 /home/joanna/.ssh/id_rsa; \
    chown joanna:joanna /home/joanna/user.txt; chmod 0644 /home/joanna/user.txt; \
    chown root:root /root/root.txt; chmod 0600 /root/root.txt; \
    chmod 0755 /usr/local/bin/openadmin-entrypoint /usr/local/bin/openadmin-healthcheck; \
    mkdir -p /run/sshd; sshd -t; apache2ctl configtest; visudo -cf /etc/sudoers
EXPOSE 22 80
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=25s --timeout=12s --start-period=45s --retries=4 \
  CMD ["/usr/local/bin/openadmin-healthcheck"]
ENTRYPOINT ["/usr/local/bin/openadmin-entrypoint"]
