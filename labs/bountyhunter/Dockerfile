# syntax=docker/dockerfile:1
# Real Apache, PHP SimpleXML/libxml, OpenSSH, sudo and Python.
# Independently reconstructed from public retired BountyHunter writeups.
FROM alpine:3.20

RUN apk add --no-cache \
      apache2 apache2-proxy bash ca-certificates curl openssh-server \
      php83 php83-fpm php83-simplexml php83-xml \
      python3 shadow sudo \
 && adduser -D -u 1000 -h /home/development -s /bin/ash development \
 && echo 'development:m19RoAU0hP41A1sTsq6K' | chpasswd \
 && mkdir -p /run/apache2 /run/php /run/sshd /opt/skytrain_inc \
             /etc/php83/php-fpm.d /etc/sudoers.d \
 && sed -i \
      -e 's/^#LoadModule proxy_module /LoadModule proxy_module /' \
      -e 's/^#LoadModule proxy_fcgi_module /LoadModule proxy_fcgi_module /' \
      -e 's/^#ServerName .*/ServerName localhost/' \
      /etc/apache2/httpd.conf \
 && rm -f /etc/php83/php-fpm.d/www.conf \
 && printf '%s\n' 'development ALL=(root) NOPASSWD: /usr/bin/python3 /opt/skytrain_inc/ticketValidator.py' \
      > /etc/sudoers.d/development \
 && chmod 0440 /etc/sudoers.d/development
COPY config/apache.conf /etc/apache2/conf.d/bountyhunter.conf
COPY config/php-fpm.conf /etc/php83/php-fpm.d/bountyhunter.conf
COPY config/sshd_config /etc/ssh/sshd_config
COPY site/ /var/www/localhost/htdocs/
COPY skytrain/ticketValidator.py /opt/skytrain_inc/ticketValidator.py
COPY skytrain/contract.txt skytrain/invalid-ticket.md /home/development/
COPY flags/user.txt /home/development/user.txt
COPY flags/root.txt /root/root.txt
COPY scripts/entrypoint.sh /usr/local/bin/bountyhunter-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/bountyhunter-healthcheck
RUN set -eu; \
    chmod 0755 /usr/local/bin/bountyhunter-*; \
    chown -R root:root /var/www/localhost/htdocs /opt/skytrain_inc; \
    chmod 0644 /var/www/localhost/htdocs/*.php; \
    chmod 0644 /var/www/localhost/htdocs/resources/*; \
    chmod 0644 /opt/skytrain_inc/ticketValidator.py; \
    chown -R development:development /home/development; \
    chmod 0640 /home/development/user.txt; \
    chmod 0600 /root/root.txt; \
    php83 -r 'if (!function_exists("simplexml_load_string")) exit(1);'; \
    php83 -l /var/www/localhost/htdocs/tracker_diRbPr00f314.php; \
    httpd -t; \
    httpd -M 2>/dev/null | grep -Fq 'proxy_module'; \
    httpd -M 2>/dev/null | grep -Fq 'proxy_fcgi_module'; \
    visudo -cf /etc/sudoers

EXPOSE 80 22
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=15s --timeout=8s --start-period=30s --retries=4 \
  CMD ["/usr/local/bin/bountyhunter-healthcheck"]
ENTRYPOINT ["/usr/local/bin/bountyhunter-entrypoint"]
