# syntax=docker/dockerfile:1.7
FROM python:3.12-alpine3.22 AS build
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /venv \
 && /venv/bin/pip install --no-cache-dir --upgrade pip \
 && /venv/bin/pip install --no-cache-dir -r requirements.txt
COPY app.py admin.py lwt.py utils.py init_db.py ./
COPY templates/ ./templates/
COPY static/ ./static/
RUN python - <<'PY'
import zipfile
from pathlib import Path
with zipfile.ZipFile("src.zip", "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name in ("app.py", "admin.py", "lwt.py", "utils.py"):
        archive.write(name, name)
    for directory in ("templates", "static"):
        for path in Path(directory).rglob("*"):
            if path.is_file():
                archive.write(path, path.as_posix())
PY
FROM python:3.12-alpine3.22 AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 INTENSE_DB=/var/lib/intense/app.db
RUN apk add --no-cache curl su-exec \
 && addgroup -S web \
 && adduser -S -D -H -G web web \
 && mkdir -p /app /app/logs /var/lib/intense /home/analyst \
 && chown -R web:web /app /var/lib/intense
WORKDIR /app
COPY --from=build /venv /venv
ENV PATH="/venv/bin:$PATH"
COPY --from=build /build/app.py /build/admin.py /build/lwt.py /build/utils.py /build/init_db.py ./
COPY --from=build /build/templates ./templates
COPY --from=build /build/static ./static
COPY --from=build /build/src.zip ./src.zip
COPY scripts/start.sh /usr/local/bin/intense-start
COPY scripts/healthcheck.sh /usr/local/bin/intense-healthcheck
RUN chmod 0755 /usr/local/bin/intense-start /usr/local/bin/intense-healthcheck \
 && chown -R root:root /app \
 && chmod -R a+rX /app
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 CMD ["/usr/local/bin/intense-healthcheck"]
ENTRYPOINT ["/usr/local/bin/intense-start"]
