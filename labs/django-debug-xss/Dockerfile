# Authentic Django technical 500-page XSS, CVE-2017-12794.
# PostgreSQL must generate the original duplicate-key exception; SQLite does not.
FROM python:3.9-alpine3.16
ARG DJANGO_VERSION=1.11.4
RUN apk add --no-cache postgresql postgresql-client su-exec libpq chromium \
 && pip install --no-cache-dir "Django==${DJANGO_VERSION}" "psycopg2-binary==2.9.9" "pyppeteer==2.0.0" \
 && addgroup -S lab && adduser -S -D -G lab lab \
 && addgroup -S reviewbot && adduser -S -D -G reviewbot reviewbot \
 && addgroup lab reviewbot \
 && mkdir -p /app /run/postgresql /var/lib/postgresql/data /run/django/reports /run/django/bot-state/profiles /opt/review \
 && chown -R postgres:postgres /run/postgresql /var/lib/postgresql \
 && chmod 0700 /var/lib/postgresql/data
WORKDIR /app
COPY app.py /app/app.py
COPY xss /app/xss
COPY start.sh /usr/local/bin/start-lab
COPY seed.py /usr/local/bin/seed-lab.py
COPY bot.py /opt/review/bot.py
RUN chmod 0755 /usr/local/bin/start-lab \
 && python -m py_compile /app/app.py
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=4s --start-period=30s --retries=3 \
 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=2)" || exit 1
ENTRYPOINT ["/usr/local/bin/start-lab"]
