FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    DB_PATH=/var/lib/credential-gate/operations.sqlite3 \
    FLAG_PATH=/opt/credential-gate/flag.txt

RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin lab \
    && install -d -o lab -g lab -m 0750 /var/lib/credential-gate \
    && install -d -o root -g lab -m 0750 /opt/credential-gate

WORKDIR /app
COPY app.py /app/app.py
COPY static/ /app/static/
COPY flags/flag.txt /opt/credential-gate/flag.txt
RUN chown root:lab /opt/credential-gate/flag.txt \
    && chmod 0440 /opt/credential-gate/flag.txt \
    && chmod -R a-w /app

USER lab
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=3).read()" || exit 1
CMD ["python", "/app/app.py"]
