# HTB Usage-inspired single-container reconstruction.
# Real MySQL 8.0, Laravel 10.18.0, encore/laravel-admin 1.8.19, nginx,
# OpenSSH, Monit and p7zip 16.02. The custom main-site source is reconstructed
# from public writeups; it is not claimed to be HTB's private source.
FROM container-registry.oracle.com/os/oraclelinux:9-slim AS app-build
RUN microdnf module enable -y php:8.1 \
 && microdnf install -y php php-cli php-common php-pdo php-mysqlnd php-mbstring \
      php-xml php-curl php-bcmath php-zip php-gd php-intl php-opcache \
      curl tar gzip unzip git ca-certificates \
 && microdnf clean all
COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer
WORKDIR /var/www/usage
RUN curl -fsSL https://codeload.github.com/laravel/laravel/tar.gz/7effeb99ec1568f006ed95e60d3e7dfeed1b8160 \
      | tar -xz --strip-components=1 \
 && test -f artisan
COPY composer.json /var/www/usage/composer.json
RUN composer update --no-dev --no-interaction --prefer-dist --no-progress --optimize-autoloader
RUN php artisan vendor:publish --provider="Encore\\Admin\\AdminServiceProvider" --tag=laravel-admin-config --force \
 && php artisan vendor:publish --provider="Encore\\Admin\\AdminServiceProvider" --tag=laravel-admin-migrations --force \
 && php artisan vendor:publish --provider="Encore\\Admin\\AdminServiceProvider" --tag=laravel-admin-assets --force
COPY app/ /var/www/usage/app/
COPY routes/web.php /var/www/usage/routes/web.php
COPY resources/views/ /var/www/usage/resources/views/
COPY config/admin.php /var/www/usage/config/admin.php
COPY database/seeders/UsageSeeder.php /var/www/usage/database/seeders/UsageSeeder.php
COPY app/Admin/ /var/www/usage/app/Admin/
RUN composer dump-autoload --no-dev --optimize \
 && php -l app/Http/Controllers/UsageController.php \
 && php -l app/Admin/routes.php

FROM container-registry.oracle.com/os/oraclelinux:9-slim AS runtime
RUN set -eux; \
    curl -fsSL https://repo.mysql.com/RPM-GPG-KEY-mysql-2023 -o /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql; \
    rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql; \
    printf '%s\n' '[mysql8.0-server-minimal]' 'name=MySQL 8.0 Server Minimal' 'enabled=1' 'baseurl=https://repo.mysql.com/yum/mysql-8.0-community/docker/el/9/$basearch/' 'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-mysql' 'module_hotfixes=true' > /etc/yum.repos.d/mysql-community.repo
RUN microdnf module enable -y php:8.1 \
 && microdnf install -y oracle-epel-release-el9 \
 && microdnf install -y mysql-community-server-minimal-8.0.46-1.el9 mysql-community-client-minimal-8.0.46-1.el9 \
 && microdnf install -y \
      php php-cli php-common php-fpm php-pdo php-mysqlnd php-mbstring php-xml \
      php-curl php-bcmath php-zip php-gd php-intl php-opcache \
      nginx openssh-server openssh-clients sudo shadow-utils procps-ng curl tar gzip unzip \
      p7zip monit openssl hostname findutils \
 && microdnf clean all \
 && mkdir -p /var/www/usage /var/lib/mysql /var/run/mysqld /var/run/php-fpm \
      /var/run/nginx /var/backups /etc/my.cnf.d /etc/sudoers.d \
 && groupadd -r dash \
 && useradd -r -u 1000 -g dash -d /home/dash -s /bin/bash dash \
 && useradd -r -u 1001 -m -s /bin/bash xander \
 && usermod -aG xander dash \
 && useradd -r -g nginx -s /sbin/nologin nginx 2>/dev/null || true
COPY --from=app-build /var/www/usage /var/www/usage
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/php-fpm.conf /etc/php-fpm.d/www.conf
COPY config/mysql.cnf /etc/my.cnf.d/usage.cnf
COPY config/sshd_config /etc/ssh/sshd_config
COPY scripts/entrypoint.sh /usr/local/bin/usage-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/usage-healthcheck
COPY LICENSE-NOTICES.md /usr/share/doc/usage/LICENSE-NOTICES.md
RUN set -eux; \
    mkdir -p /var/www/usage/public/uploads/images /var/www/usage/storage /var/www/usage/bootstrap/cache \
             /home/dash/.ssh /var/backups /run/sshd /run/php-fpm /run/nginx; \
    chown -R root:xander /var/www/usage; \
    chmod -R 0755 /var/www/usage; \
    chown -R dash:xander /var/www/usage/storage /var/www/usage/bootstrap/cache /var/www/usage/public/uploads; \
    chmod 0775 /var/www/usage/public /var/www/usage/public/uploads /var/www/usage/public/uploads/images; \
    chmod -R 0775 /var/www/usage/storage /var/www/usage/bootstrap/cache; \
    chown root:root /etc/sudoers.d; \
    printf '%s\n' 'xander ALL=(root) NOPASSWD: /usr/bin/7za a /var/backups/project.zip -tzip -snl -mmt -- *' > /etc/sudoers.d/usage; \
    chmod 0440 /etc/sudoers.d/usage; \
    visudo -cf /etc/sudoers; \
    test -x /usr/bin/7za; \
    /usr/bin/7za | head -n 2; \
    php-fpm --test; \
    nginx -t; \
    mysqld --version | grep -F '8.0.'; \
    php -v | head -n 1 | grep -F '8.1.'; \
    chmod 0755 /usr/local/bin/usage-entrypoint /usr/local/bin/usage-healthcheck
EXPOSE 22 80
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=15s --timeout=8s --start-period=90s --retries=4 CMD ["/usr/local/bin/usage-healthcheck"]
ENTRYPOINT ["/usr/local/bin/usage-entrypoint"]
