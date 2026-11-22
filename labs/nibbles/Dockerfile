# syntax=docker/dockerfile:1.7
# Authentic Nibbleblog 4.0.3 historical app, isolated Linux Docker lab.
FROM alpine:3.15 AS upstream
RUN apk add --no-cache ca-certificates curl tar
ARG NIBBLEBLOG_REV=6fe138276e82ed604bb35a960327a4ac0b485097
RUN set -eux; \
    curl -fL --retry 4 --connect-timeout 20 \
      "https://codeload.github.com/dignajar/nibbleblog/tar.gz/$NIBBLEBLOG_REV" \
      -o /tmp/nibbleblog.tar.gz; \
    mkdir -p /opt/nibbleblog /tmp/upstream; \
    tar -xzf /tmp/nibbleblog.tar.gz -C /tmp/upstream; \
    cp -a "/tmp/upstream/nibbleblog-$NIBBLEBLOG_REV/." /opt/nibbleblog/; \
    grep -Fq "'4.0.3'" /opt/nibbleblog/admin/boot/rules/98-constants.bit; \
    grep -Fq 'move_uploaded_file' /opt/nibbleblog/admin/controllers/plugins/config.bit; \
    test -s /opt/nibbleblog/LICENSE.txt

FROM alpine:3.15
RUN apk add --no-cache \
    apache2 php7 php7-apache2 php7-dom php7-simplexml php7-xml \
    php7-gd php7-session php7-json php7-mbstring php7-ctype \
    php7-iconv php7-fileinfo php7-openssl \
    openssh sudo bash unzip ca-certificates
RUN set -eux; \
    addgroup -g 1001 nibbler; \
    adduser -D -u 1001 -G nibbler -h /home/nibbler -s /bin/sh nibbler; \
    mkdir -p /run/apache2 /run/sshd /var/www/localhost/htdocs/nibbleblog; \
    sed -ri 's/^User[[:space:]]+apache/User nibbler/;s/^Group[[:space:]]+apache/Group nibbler/' /etc/apache2/httpd.conf; \
    printf '%s\n' \
      '<Directory "/var/www/localhost/htdocs">' \
      '    Options FollowSymLinks' \
      '    AllowOverride All' \
      '    Require all granted' \
      '</Directory>' > /etc/apache2/conf.d/nibbles-site.conf; \
    printf '%s\n' 'nibbler ALL=(root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh' \
      > /etc/sudoers.d/nibbler; \
    chmod 0440 /etc/sudoers.d/nibbler; \
    mkdir -p /etc/ssh/sshd_config.d; \
    printf '%s\n' \
      'PermitRootLogin no' \
      'PasswordAuthentication no' \
      'KbdInteractiveAuthentication no' \
      'PubkeyAuthentication yes' \
      > /etc/ssh/sshd_config.d/90-nibbles.conf; \
    sed -i '1iInclude /etc/ssh/sshd_config.d/*.conf' /etc/ssh/sshd_config
COPY --from=upstream /opt/nibbleblog/ /var/www/localhost/htdocs/nibbleblog/
COPY site/index.html /var/www/localhost/htdocs/index.html
COPY scripts/bootstrap.php /tmp/nibbles-bootstrap.php
COPY scripts/entrypoint.sh /usr/local/bin/nibbles-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/nibbles-healthcheck
COPY flags/user.txt /home/nibbler/user.txt
COPY flags/root.txt /root/root.txt
# Run genuine upstream installer. No replacement PHP authentication or upload code.
RUN set -eux; \
    cd /var/www/localhost/htdocs/nibbleblog; \
    php7 -d display_errors=1 /tmp/nibbles-bootstrap.php >/tmp/nibbles-bootstrap.log; \
    test -s content/private/config.xml; \
    test -s content/private/users.xml; \
    test -s content/private/shadow.php; \
    sed -i 's/^Version: Beta on Github$/Version: v4.0.3/' README; \
    sed -i 's/^Codename:$/Codename: Coffee/' README; \
    sed -i 's/^Release date:$/Release date: 2014-04-01/' README; \
    chown -R nibbler:nibbler /var/www/localhost/htdocs/nibbleblog /home/nibbler; \
    chmod 0644 /home/nibbler/user.txt; \
    chmod 0600 /root/root.txt; \
    chmod 0755 /usr/local/bin/nibbles-entrypoint /usr/local/bin/nibbles-healthcheck; \
    rm -f /tmp/nibbles-bootstrap.php /tmp/nibbles-bootstrap.log; \
    php7 -l /var/www/localhost/htdocs/nibbleblog/admin.php
# The genuine privilege issue is a writable script path in a sudoers rule.
# The original personal.zip is not publicly distributed, so seed an ordinary
# monitoring script in its expected archive structure, *not* a fake suid tool.
RUN set -eux; \
    apk add --no-cache --virtual .archive-build zip; \
    mkdir -p /tmp/monitor-archive/personal/stuff; \
    printf '%s\n' '#!/bin/sh' 'echo "System monitoring"' 'uptime' 'df -h /' \
      > /tmp/monitor-archive/personal/stuff/monitor.sh; \
    chmod 0755 /tmp/monitor-archive/personal/stuff/monitor.sh; \
    ( cd /tmp/monitor-archive && zip -q -r /home/nibbler/personal.zip personal ); \
    chown nibbler:nibbler /home/nibbler/personal.zip; \
    rm -rf /tmp/monitor-archive; \
    apk del .archive-build
EXPOSE 22 80
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=20s --timeout=5s --start-period=20s --retries=3 \
 CMD ["/usr/local/bin/nibbles-healthcheck"]
ENTRYPOINT ["/usr/local/bin/nibbles-entrypoint"]
