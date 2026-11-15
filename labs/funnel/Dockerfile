# Stage 1: generate the actual PDF document exposed through anonymous FTP.
FROM python:3.12-alpine AS assets
WORKDIR /work
COPY assets/build_policy.py /work/build_policy.py
RUN python /work/build_policy.py /work/password_policy.pdf

# Stage 2: only services required by the laboratory (no Python/build tools).
FROM debian:bookworm-slim AS runtime
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash ca-certificates openssh-server openssh-client vsftpd postgresql-15 postgresql-client-15 \
 && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /usr/share/doc/* /usr/share/man/* \
 && mkdir -p /run/sshd /srv/ftp/mail_backup /opt/funnel /var/run/vsftpd/empty

COPY --from=assets /work/password_policy.pdf /srv/ftp/mail_backup/password_policy.pdf
COPY assets/welcome_28112022 /srv/ftp/mail_backup/welcome_28112022
COPY config/vsftpd.conf /etc/vsftpd.conf
COPY config/sshd-funnel.conf /etc/ssh/sshd_config.d/60-funnel.conf
COPY scripts/entrypoint.sh /usr/local/bin/funnel-entrypoint
COPY scripts/healthcheck.sh /usr/local/bin/funnel-healthcheck
# The lab flag lives OUTSIDE application source and is copied into the image at build time.
COPY flags/flag.txt /opt/funnel/flag.txt
RUN chmod 755 /usr/local/bin/funnel-entrypoint /usr/local/bin/funnel-healthcheck \
 && chmod 600 /opt/funnel/flag.txt \
 && chown -R root:root /srv/ftp \
 && chmod -R a-w /srv/ftp \
 && chmod 755 /srv/ftp /srv/ftp/mail_backup \
 && chmod 644 /srv/ftp/mail_backup/* \
 && useradd -m -s /bin/bash christine \
 && useradd -m -s /bin/bash optimus \
 && useradd -m -s /bin/bash albert \
 && useradd -m -s /bin/bash andreas \
 && useradd -m -s /bin/bash maria \
 && echo 'christine:funnel123#!#' | chpasswd \
 && passwd -l optimus && passwd -l albert && passwd -l andreas && passwd -l maria \
 && rm -rf /var/log/apt/* /var/log/dpkg.log
EXPOSE 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=8s --start-period=45s --retries=3 CMD ["/usr/local/bin/funnel-healthcheck"]
ENTRYPOINT ["/usr/local/bin/funnel-entrypoint"]
