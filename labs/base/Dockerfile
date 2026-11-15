# PHP 7.2 is intentional: the original challenge relies on its legacy
# strcmp(array, string) warning/NULL behavior for the authentication bypass.
FROM php:7.2-apache

ENV DEBIAN_FRONTEND=noninteractive

# PHP 7.2's official image is based on an archived Debian release. Point APT
# at Debian's archive so the legacy SSH and sudo packages remain installable.
RUN set -eux; \
    sed -i \
      -e 's|deb.debian.org/debian|archive.debian.org/debian|g' \
      -e 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' \
      /etc/apt/sources.list; \
    printf '%s\n' 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99archive; \
    apt-get update; \
    apt-get install -y --no-install-recommends openssh-server sudo vim-tiny; \
    rm -rf /var/lib/apt/lists/*

# John reuses the password disclosed in the web application's config.php.
RUN set -eux; \
    useradd --create-home --shell /bin/bash john; \
    echo 'john:thisisagoodpassword' | chpasswd; \
    printf '%s\n' 'john ALL=(root) /usr/bin/find' > /etc/sudoers.d/john-find; \
    chmod 0440 /etc/sudoers.d/john-find; \
    mkdir -p /home/john /var/run/sshd /var/www/html/_uploaded; \
    sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config; \
    sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config; \
    printf '\nAllowUsers john\n' >> /etc/ssh/sshd_config; \
    visudo -cf /etc/sudoers

# Copy flags from external files
COPY user_flag.txt /home/john/user.txt
COPY root_flag.txt /root/root.txt
RUN chown john:john /home/john/user.txt && chmod 0644 /home/john/user.txt && \
    chown root:root /root/root.txt && chmod 0600 /root/root.txt

COPY apache-base.conf /etc/apache2/conf-available/base-lab.conf
RUN a2enconf base-lab && a2enmod autoindex

COPY public/ /var/www/html/
RUN set -eux; \
    mkdir -p /var/www/html/_uploaded; \
    chown -R www-data:www-data /var/www/html/_uploaded; \
    chmod 0755 /var/www/html/_uploaded; \
    chmod 0644 /var/www/html/login/login.php.swp

COPY entrypoint.sh /usr/local/bin/base-entrypoint
RUN chmod 0755 /usr/local/bin/base-entrypoint

EXPOSE 80 22

HEALTHCHECK --interval=5s --timeout=3s --retries=3 --start-period=5s \
  CMD php -r "exit(@file_get_contents('http://127.0.0.1/') !== false ? 0 : 1);"

ENTRYPOINT ["/usr/local/bin/base-entrypoint"]
