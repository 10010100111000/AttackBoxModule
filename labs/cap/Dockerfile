# syntax=docker/dockerfile:1.7
# Cap: real vsftpd + SSH + Flask/Gunicorn + tcpdump + Python file capabilities.
# Stage 1 creates the seeded PCAP from a real FTP session, not crafted packets.
FROM python:3.8-alpine3.18 AS pcap-builder
RUN apk add --no-cache vsftpd tcpdump
RUN set -eux; \
    adduser -D -u 1000 -h /home/nathan -s /bin/sh nathan; \
    echo 'nathan:Buck3tH4TF0RM3!' | chpasswd; \
    mkdir -p /var/run/vsftpd/empty /pcaps; \
    printf '%s\n' \
      'listen=YES' \
      'listen_ipv6=NO' \
      'listen_address=127.0.0.1' \
      'listen_port=2121' \
      'background=NO' \
      'anonymous_enable=NO' \
      'local_enable=YES' \
      'write_enable=NO' \
      'local_umask=022' \
      'chroot_local_user=NO' \
      'pam_service_name=vsftpd' \
      'secure_chroot_dir=/var/run/vsftpd/empty' \
      'seccomp_sandbox=NO' \
      'xferlog_enable=NO' \
      > /tmp/vsftpd-pcap.conf; \
    tcpdump -i lo -U -w /pcaps/0.pcap 'tcp port 2121' >/tmp/tcpdump.log 2>&1 & \
    capture_pid=$!; \
    /usr/sbin/vsftpd /tmp/vsftpd-pcap.conf >/tmp/vsftpd.log 2>&1 & \
    ftp_pid=$!; \
    sleep 1; \
    python3.8 -c 'import socket; s=socket.create_connection(("127.0.0.1",2121),5); f=s.makefile("rwb"); assert f.readline().startswith(b"220"); f.write(b"USER nathan\\r\\n"); f.flush(); assert f.readline().startswith(b"331"); f.write(b"PASS Buck3tH4TF0RM3!\\r\\n"); f.flush(); assert f.readline().startswith(b"230"); f.write(b"QUIT\\r\\n"); f.flush(); f.readline(); s.close()'; \
    sleep 1; \
    kill -INT "$capture_pid"; \
    wait "$capture_pid"; \
    kill "$ftp_pid" 2>/dev/null || true; \
    wait "$ftp_pid" 2>/dev/null || true; \
    test -s /pcaps/0.pcap; \
    tcpdump -nn -A -r /pcaps/0.pcap 2>/dev/null | grep -Fq 'USER nathan'; \
    tcpdump -nn -A -r /pcaps/0.pcap 2>/dev/null | grep -Fq 'PASS Buck3tH4TF0RM3!'

FROM python:3.8-alpine3.18 AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apk add --no-cache openssh vsftpd tcpdump iproute2 net-tools libcap-utils bash su-exec \
 && adduser -D -u 1000 -h /home/nathan -s /bin/bash nathan \
 && mkdir -p /run/sshd /var/run/vsftpd/empty /pcaps /app/templates \
 && ln /usr/local/bin/python3.8 /usr/bin/python3.8 \
 && setcap cap_setuid,cap_net_bind_service+eip /usr/bin/python3.8 \
 && getcap /usr/bin/python3.8 | grep -F 'cap_setuid,cap_net_bind_service'
COPY --from=pcap-builder /pcaps/0.pcap /pcaps/0.pcap
COPY app.py /app/app.py
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY requirements.txt /app/requirements.txt
COPY config/vsftpd.conf /etc/vsftpd.conf
COPY config/sshd_config /etc/ssh/sshd_config
COPY scripts/entrypoint.sh /usr/local/bin/cap-entrypoint
COPY scripts/healthcheck.py /usr/local/bin/cap-healthcheck.py
COPY flags/user.txt /home/nathan/user.txt
COPY flags/root.txt /root/root.txt
RUN pip install --no-cache-dir --disable-pip-version-check -r /app/requirements.txt \
 && chown -R nathan:nathan /home/nathan \
 && chmod 0400 /home/nathan/user.txt \
 && chmod 0600 /root/root.txt \
 && chmod 0755 /usr/local/bin/cap-entrypoint /usr/local/bin/cap-healthcheck.py \
 && chown root:root /pcaps /pcaps/0.pcap \
 && chmod 0755 /pcaps \
 && chmod 0644 /pcaps/0.pcap \
 && /usr/sbin/sshd -t
WORKDIR /app
EXPOSE 21 22 80 30000-30009
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=20s --timeout=8s --start-period=25s --retries=3 \
 CMD ["/usr/bin/python3.8", "/usr/local/bin/cap-healthcheck.py"]
ENTRYPOINT ["/usr/local/bin/cap-entrypoint"]
