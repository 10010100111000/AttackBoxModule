FROM php:8.2-alpine3.23
RUN apk add --no-cache chromium-headless-shell python3 py3-pip su-exec curl \
 && python3 -m pip install --no-cache-dir --break-system-packages --target=/opt/alert/deps markdown==3.7 pyppeteer==2.0.0 \
 && addgroup -S alertbot && adduser -S -D -G alertbot -h /home/alertbot alertbot \
 && mkdir -p /srv/alert/uploads /srv/alert/messages /run/alert/queue /run/alert/profiles /opt/alert/private /home/alertbot \
 && chown www-data:www-data /srv/alert/uploads \
 && chown www-data:alertbot /srv/alert/messages && chmod 2750 /srv/alert/messages \
 && chown -R alertbot:alertbot /run/alert/profiles /home/alertbot \
 && chown www-data:alertbot /run/alert/queue && chmod 2770 /run/alert/queue
WORKDIR /srv/alert
COPY site/ /srv/alert/
COPY bot/ /opt/alert/bot/
COPY scripts/ /opt/alert/scripts/
COPY flags/user.txt /opt/alert/private/web-flag.txt
RUN chmod 0755 /opt/alert/scripts/start.sh && chown www-data:www-data /opt/alert/private/web-flag.txt \
 && chmod 0600 /opt/alert/private/web-flag.txt \
 && php -l /srv/alert/index.php && php -l /srv/alert/visualizer.php \
 && php -l /srv/alert/contact.php && php -l /srv/alert/messages.php \
 && python3 -m py_compile /opt/alert/bot/review.py /opt/alert/scripts/render_md.py
ENV PYTHONPATH=/opt/alert/deps
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=5s --start-period=35s --retries=3 CMD ["sh","-c","curl -fsS http://127.0.0.1:8080/index.php >/dev/null && test -f /run/alert/profiles/bot.ready"]
ENTRYPOINT ["/opt/alert/scripts/start.sh"]
