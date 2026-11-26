# syntax=docker/dockerfile:1.7
FROM python:3.11.2-slim-bookworm AS python-deps
WORKDIR /build
RUN pip install --no-cache-dir --target=/opt/python-deps \
      Flask==2.2.2 Werkzeug==2.2.2 itsdangerous==2.1.2 playwright==1.44.0

FROM python:3.11.2-slim-bookworm AS runtime
ENV PYTHONPATH=/opt/python-deps PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates chromium coreutils curl findutils iproute2 openssh-server procps sudo supervisor \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 1000 dvir \
 && useradd --uid 1000 --gid 1000 --create-home --home-dir /home/dvir --shell /bin/bash dvir \
 && mkdir -p /run/sshd /run/supervisor /home/dvir/app/hacking_reports /var/mail \
 && touch /var/mail/dvir \
 && chmod 0644 /var/mail/dvir \
 && chown -R dvir:dvir /home/dvir

COPY --from=python-deps /opt/python-deps /opt/python-deps
COPY app/ /home/dvir/app/
COPY config/supervisord.conf /etc/supervisor/conf.d/headless.conf
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/sudoers-dvir /etc/sudoers.d/dvir
COPY config/dvir-mail /var/mail/dvir
COPY scripts/entrypoint.sh /usr/local/bin/headless-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/headless-healthcheck
COPY scripts/syscheck /usr/bin/syscheck

RUN set -eu; \
    chown -R dvir:dvir /home/dvir/app; \
    chmod 0755 /home/dvir/app; \
    chmod 0755 /home/dvir/app/app.py /home/dvir/app/inspect_reports.py /home/dvir/app/report.sh; \
    chown -R dvir:dvir /home/dvir/app/hacking_reports; \
    chmod 0700 /home/dvir/app/hacking_reports; \
    chown root:root /usr/bin/syscheck /etc/sudoers.d/dvir; \
    chmod 0755 /usr/bin/syscheck /usr/local/bin/headless-entrypoint /usr/local/bin/headless-healthcheck; \
    chmod 0440 /etc/sudoers.d/dvir; \
    visudo -cf /etc/sudoers; \
    ssh-keygen -A

WORKDIR /home/dvir/app
EXPOSE 22/tcp 5000/tcp
HEALTHCHECK --interval=20s --timeout=6s --start-period=35s --retries=3 CMD ["/usr/local/bin/headless-healthcheck"]
ENTRYPOINT ["/usr/local/bin/headless-entrypoint"]
