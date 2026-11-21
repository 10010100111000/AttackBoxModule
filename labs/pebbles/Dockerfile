# syntax=docker/dockerfile:1.7
# Real historical OffSec PG Pebbles reference stack. Isolated Linux Docker only.
FROM alpine:3.20 AS tomcat-artifact
RUN apk add --no-cache ca-certificates curl tar coreutils
ARG TOMCAT_VERSION=9.0.30
ARG TOMCAT_SHA512=40bf428a534816317e5e8732b679e6d73f6ed977aab4ac5e2b9eaf1eb087eaa68a18b0fd3da8c39ca4b96f5b6fd919dec84517abba0d5e797285ade934a92990
RUN set -eux; \
    curl -fL --retry 3 --connect-timeout 15 --output /tmp/tomcat.tar.gz \
      "https://archive.apache.org/dist/tomcat/tomcat-9/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz"; \
    printf '%s  %s\n' "$TOMCAT_SHA512" /tmp/tomcat.tar.gz | sha512sum -c -; \
    mkdir -p /opt/tomcat; \
    tar -xzf /tmp/tomcat.tar.gz --strip-components=1 -C /opt/tomcat; \
    test -f /opt/tomcat/RELEASE-NOTES

FROM ubuntu:16.04 AS runtime
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 \
    CATALINA_HOME=/opt/tomcat \
    CATALINA_BASE=/opt/tomcat \
    JAVA_OPTS="-Xms32m -Xmx128m -Djava.security.egd=file:/dev/./urandom" \
    PEBBLES_MYSQL_BOOTSTRAP=pebbles-bootstrap-only \
    PEBBLES_ZM_PASSWORD=zmpass

# Xenial is EOL: use signed historical Ubuntu archives, retaining signature checks.
RUN set -eux; \
    printf '%s\n' \
      'deb http://old-releases.ubuntu.com/ubuntu/ xenial main restricted universe multiverse' \
      'deb http://old-releases.ubuntu.com/ubuntu/ xenial-updates main restricted universe multiverse' \
      'deb http://old-releases.ubuntu.com/ubuntu/ xenial-security main restricted universe multiverse' \
      > /etc/apt/sources.list; \
    printf '%s\n' 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99-lab-archive; \
    printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d; \
    chmod 0755 /usr/sbin/policy-rc.d; \
    printf '%s\n' \
      'mysql-server-5.7 mysql-server/root_password password pebbles-bootstrap-only' \
      'mysql-server-5.7 mysql-server/root_password_again password pebbles-bootstrap-only' \
      'mysql-server mysql-server/root_password password pebbles-bootstrap-only' \
      'mysql-server mysql-server/root_password_again password pebbles-bootstrap-only' \
      | debconf-set-selections; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      apache2 libapache2-mod-php7.0 php7.0-cli php7.0-mysql php7.0-gd php7.0-mbstring \
      php7.0-xml php7.0-curl mysql-server-5.7 mysql-client-5.7 \
      zoneminder=1.29.0+dfsg-1ubuntu2 vsftpd openssh-server \
      openjdk-8-jre-headless ca-certificates curl procps \
      netcat-openbsd util-linux; \
    dpkg-query -W -f='${Version}\n' zoneminder | grep -Fx '1.29.0+dfsg-1ubuntu2'; \
    dpkg-query -W -f='${Version}\n' mysql-server-5.7 | grep -E '^5[.]7[.]'; \
    test -f /usr/share/zoneminder/www/index.php; \
    test -f /usr/share/zoneminder/db/zm_create.sql; \
    test -f /usr/share/zoneminder/www/ajax/log.php; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb

COPY --from=tomcat-artifact /opt/tomcat/ /opt/tomcat/
COPY site80/public/ /var/www/pebbles/
COPY config/apache-pebbles.conf /etc/apache2/sites-available/pebbles.conf
COPY config/pebbles-vsftpd.conf /etc/vsftpd.conf
COPY config/sshd-pebbles.conf /etc/ssh/sshd_config.d/60-pebbles.conf
COPY scripts/entrypoint.sh /usr/local/bin/pebbles-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/pebbles-healthcheck
COPY flags/root.txt /root/proof.txt
RUN set -eux; \
    useradd --system --user-group --home /opt/tomcat --shell /usr/sbin/nologin tomcat; \
    mkdir -p /run/mysqld /run/sshd /run/zm /var/log/mysql /var/log/zoneminder \
      /var/www/pebbles /opt/tomcat/temp /opt/tomcat/logs /opt/tomcat/work; \
    chown -R tomcat:tomcat /opt/tomcat; \
    sed -i 's/port="8080" protocol="HTTP\/1.1"/port="18080" address="127.0.0.1" protocol="HTTP\/1.1"/' /opt/tomcat/conf/server.xml; \
    test "$(grep -c 'port="18080"' /opt/tomcat/conf/server.xml)" -eq 1; \
    test -f /var/www/html/index.html; \
    a2dissite 000-default; \
    a2ensite pebbles; \
    a2enmod cgi rewrite proxy proxy_http headers; \
    a2enconf zoneminder; \
    chmod 0755 /usr/local/bin/pebbles-entrypoint /usr/local/bin/pebbles-healthcheck; \
    chmod 0600 /root/proof.txt; \
    chown root:root /root/proof.txt; \
    sed -ri '/^[[:space:]]*user[[:space:]]*=[[:space:]]*mysql([[:space:]]*#.*)?$/d' /etc/mysql/mysql.conf.d/mysqld.cnf; \
    if grep -Eq '^[[:space:]]*user[[:space:]]*=' /etc/mysql/mysql.conf.d/mysqld.cnf; then exit 1; fi; \
    chown root:www-data /etc/zm/zm.conf; \
    chmod 0640 /etc/zm/zm.conf; \
    chown -R www-data:www-data /usr/share/zoneminder; \
    chown -R root:root /var/lib/mysql; \
    chmod 0755 /var/www/html; \
    printf 'date.timezone = UTC\n' > /etc/php/7.0/apache2/conf.d/99-pebbles-timezone.ini; \
    ln -sf /opt/tomcat/RELEASE-NOTES /opt/tomcat/webapps/ROOT/RELEASE-NOTES.txt

EXPOSE 21 22 80 3305 8080
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=30s --timeout=12s --start-period=180s --retries=4 \
  CMD ["/usr/local/bin/pebbles-healthcheck"]
ENTRYPOINT ["/usr/local/bin/pebbles-entrypoint"]
