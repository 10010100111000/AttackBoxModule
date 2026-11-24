FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive APACHE_RUN_DIR=/var/run/apache2 APACHE_LOCK_DIR=/var/lock/apache2 APACHE_LOG_DIR=/var/log/apache2 ZIPPING_USER_FLAG=""
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends apache2 libapache2-mod-php8.2 php8.2-cli php8.2-mysql php8.2-zip mariadb-server p7zip-full ca-certificates curl; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /usr/share/doc/* /usr/share/man/*; \
    sed -i 's/Listen 80/Listen 8080/g' /etc/apache2/ports.conf; \
    sed -i 's/:80>/:8080>/g' /etc/apache2/sites-enabled/000-default.conf; \
    printf '%s\n' '<Directory /var/www/html>' '  Options FollowSymLinks' '  AllowOverride None' '  Require all granted' '</Directory>' > /etc/apache2/conf-available/zipping.conf; \
    a2enconf zipping; \
    mkdir -p /run/mysqld /data/mysql /var/www/html/uploads /home/rektsu; \
    chown mysql:mysql /run/mysqld /data/mysql; \
    chown www-data:www-data /var/www/html/uploads /home/rektsu
COPY site/ /var/www/html/
COPY db/init.sql /opt/zipping/init.sql
COPY scripts/start.sh /usr/local/bin/zipping-start
COPY scripts/healthcheck.sh /usr/local/bin/zipping-healthcheck
COPY flags/user.txt /home/rektsu/user.txt
RUN chmod 0755 /usr/local/bin/zipping-start /usr/local/bin/zipping-healthcheck; \
    chown www-data:www-data /home/rektsu/user.txt; \
    chmod 0400 /home/rektsu/user.txt; \
    chown -R root:root /var/www/html; \
    chown www-data:www-data /var/www/html/uploads
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=5s --start-period=60s --retries=4 CMD ["/usr/local/bin/zipping-healthcheck"]
ENTRYPOINT ["/usr/local/bin/zipping-start"]
