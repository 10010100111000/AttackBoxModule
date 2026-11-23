# syntax=docker/dockerfile:1.7
# Isolated Editorial reconstruction. The SSRF is real; GitPython 3.1.29 is
# deliberately pinned at an authentically vulnerable release (CVE-2022-24439).
FROM python:3.11-slim-bookworm AS wheelhouse
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels -r /tmp/requirements.txt

FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends nginx openssh-server sudo git ca-certificates; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*; \
    useradd -m -s /bin/bash dev; \
    useradd -m -s /bin/bash prod; \
    echo 'dev:dev080217_devAPI!@' | chpasswd; \
    echo 'prod:080217_Producti0n_2023!@' | chpasswd; \
    mkdir -p /run/sshd /var/www/editorial/uploads /home/dev/apps \
      /opt/editorial/static /opt/editorial/templates /opt/internal_apps/clone_changes; \
    chmod 0755 /var/www/editorial /var/www/editorial/uploads; \
    chown www-data:www-data /var/www/editorial/uploads; \
    sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/; s/^#?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config; \
    printf '\nAllowUsers dev prod\n' >> /etc/ssh/sshd_config; \
    rm -f /etc/nginx/sites-enabled/default; \
    printf '%s\n' 'prod ALL=(root) NOPASSWD: /usr/local/bin/python3 /opt/internal_apps/clone_changes/clone_prod_change.py *' > /etc/sudoers.d/editorial-prod; \
    chmod 0440 /etc/sudoers.d/editorial-prod
COPY --from=wheelhouse /wheels /tmp/wheels
COPY requirements.txt /opt/editorial/requirements.txt
RUN pip install --no-index --no-cache-dir --find-links=/tmp/wheels -r /opt/editorial/requirements.txt \
    && rm -rf /tmp/wheels
COPY config/nginx.conf /etc/nginx/conf.d/editorial.conf
COPY app/public_app.py app/api_app.py /opt/editorial/
COPY site/ /opt/editorial/
COPY scripts/entrypoint.sh /usr/local/bin/editorial-entrypoint
COPY scripts/healthcheck.py /usr/local/bin/editorial-healthcheck
COPY scripts/clone_prod_change.py /opt/internal_apps/clone_changes/clone_prod_change.py
COPY flags/user.txt /home/dev/user.txt
COPY flags/root.txt /root/root.txt
RUN set -eux; \
    chmod 0755 /usr/local/bin/editorial-entrypoint /usr/local/bin/editorial-healthcheck; \
    chmod 0755 /opt/internal_apps/clone_changes/clone_prod_change.py; \
    chmod 0644 /home/dev/user.txt; chown dev:dev /home/dev/user.txt; \
    chmod 0600 /root/root.txt; chown root:root /root/root.txt; \
    chmod 0755 /opt/editorial /opt/editorial/static /opt/editorial/templates; \
    git -C /home/dev/apps init -q; \
    git -C /home/dev/apps config user.name 'Editorial API Team'; \
    git -C /home/dev/apps config user.email 'api@tiempoarriba.htb'; \
    printf '%s\n' '# Editorial API deployment notes' \
       'production_login = "prod"' \
       'production_password = "080217_Producti0n_2023!@"' \
       'release = "api v1"' > /home/dev/apps/api_notes.py; \
    git -C /home/dev/apps add api_notes.py; \
    git -C /home/dev/apps commit -qm 'initial API team notes'; \
    printf '%s\n' '# Editorial API deployment notes' \
       '# ops credentials moved out of active source' \
       'release = "api v2"' > /home/dev/apps/api_notes.py; \
    git -C /home/dev/apps commit -qam 'remove credentials from current notes'; \
    chown -R dev:dev /home/dev/apps; \
    chmod 0755 /home/dev /home/dev/apps; \
    python -c 'import git; assert git.__version__ == "3.1.29"'; \
    /usr/local/bin/python3 -m py_compile /opt/editorial/public_app.py /opt/editorial/api_app.py /opt/internal_apps/clone_changes/clone_prod_change.py; \
    nginx -t; /usr/sbin/sshd -t; visudo -cf /etc/sudoers.d/editorial-prod
WORKDIR /opt/editorial
EXPOSE 80 22
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=20s --timeout=6s --start-period=20s --retries=3 CMD ["python","/usr/local/bin/editorial-healthcheck"]
ENTRYPOINT ["/usr/local/bin/editorial-entrypoint"]
