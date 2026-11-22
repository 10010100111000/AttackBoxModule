# syntax=docker/dockerfile:1.7
# Authentic GNU Bash 4.3 pre-Shellshock-patch build; isolated lab only.
FROM alpine:3.15 AS bash43-build
RUN apk add --no-cache build-base ca-certificates curl tar
ARG BASH43_SHA256=afc687a28e0e24dc21b988fa159ff9dbcf6b7caa92ade8645cc6d5605cd024d4
RUN set -eux; \
    curl -fL --retry 4 --connect-timeout 20 \
      https://ftp.gnu.org/gnu/bash/bash-4.3.tar.gz -o /tmp/bash-4.3.tar.gz; \
    echo "$BASH43_SHA256  /tmp/bash-4.3.tar.gz" | sha256sum -c -; \
    mkdir /src; tar -xzf /tmp/bash-4.3.tar.gz -C /src; \
    cd /src/bash-4.3; \
    ./configure --without-bash-malloc --disable-nls --prefix=/usr/local; \
    make -j2; \
    cp bash /tmp/bash43; \
    env 'SHELLSHOCK_PROBE=() { :;}; echo SHELLSHOCK_NATIVE_EXECUTION' \
        /tmp/bash43 -c 'true' > /tmp/bash43-proof; \
    grep -Fq SHELLSHOCK_NATIVE_EXECUTION /tmp/bash43-proof; \
    strip /tmp/bash43; \
    test -f COPYING

FROM alpine:3.15
RUN apk add --no-cache apache2 openssh sudo perl ncurses-libs ca-certificates
RUN set -eux; \
    addgroup -g 1001 shelly; \
    adduser -D -u 1001 -G shelly -h /home/shelly -s /bin/sh shelly; \
    mkdir -p /run/apache2 /run/sshd /usr/lib/cgi-bin; \
    sed -ri 's/^User[[:space:]]+apache/User shelly/;s/^Group[[:space:]]+apache/Group shelly/' /etc/apache2/httpd.conf; \
    # Alpine httpd.conf already has /cgi-bin ScriptAlias; remove only that
    # default mapping so our genuine Apache CGI script is the one dispatched.
    sed -ri '/^[[:space:]]*ScriptAlias[[:space:]]+"?\/cgi-bin\//d' /etc/apache2/httpd.conf; \
    printf '%s\n' 'shelly ALL=(root) NOPASSWD: /usr/bin/perl' > /etc/sudoers.d/shelly; \
    chmod 0440 /etc/sudoers.d/shelly; \
    mkdir -p /etc/ssh/sshd_config.d; \
    printf '%s\n' 'Port 2222' 'PasswordAuthentication no' \
      'PermitRootLogin no' 'KbdInteractiveAuthentication no' \
      > /etc/ssh/sshd_config.d/90-shocker.conf; \
    sed -i '1iInclude /etc/ssh/sshd_config.d/*.conf' /etc/ssh/sshd_config
COPY --from=bash43-build /tmp/bash43 /usr/local/bin/bash43
COPY --from=bash43-build /src/bash-4.3/COPYING /usr/share/licenses/bash43/COPYING
COPY site/index.html /var/www/localhost/htdocs/index.html
COPY site/shocker-cgi.conf /etc/apache2/conf.d/shocker-cgi.conf
COPY site/user.sh /usr/lib/cgi-bin/user.sh
COPY scripts/entrypoint.sh /usr/local/bin/shocker-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/shocker-healthcheck
COPY flags/user.txt /home/shelly/user.txt
COPY flags/root.txt /root/root.txt
RUN set -eux; \
    chmod 0755 /usr/local/bin/bash43 /usr/lib/cgi-bin/user.sh \
      /usr/local/bin/shocker-entrypoint /usr/local/bin/shocker-healthcheck; \
    chown -R shelly:shelly /home/shelly; \
    chmod 0644 /home/shelly/user.txt; chmod 0600 /root/root.txt; \
    /usr/sbin/httpd -t; \
    grep -Fq 'ScriptAlias /cgi-bin/ "/usr/lib/cgi-bin/"' /etc/apache2/conf.d/shocker-cgi.conf; \
    env 'SHOCKER_NATIVE=() { :;}; echo CVE2014_6271_REAL' \
      /usr/local/bin/bash43 -c 'true' | grep -Fq CVE2014_6271_REAL
EXPOSE 80 2222
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=20s --timeout=6s --start-period=20s --retries=3 \
 CMD ["/usr/local/bin/shocker-healthcheck"]
ENTRYPOINT ["/usr/local/bin/shocker-entrypoint"]
