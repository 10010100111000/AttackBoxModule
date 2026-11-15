# Stage 1: fetch the official open-source Volt Flask/Jinja UI source.
FROM alpine:3.20 AS volt-source
ARG VOLT_COMMIT=53c8718aeade16f0058c8bcaac2bc1bee1dbffbf
RUN apk add --no-cache git ca-certificates \
 && git init /src \
 && git -C /src remote add origin https://github.com/app-generator/jinja-volt-dashboard.git \
 && git -C /src fetch --depth=1 origin "$VOLT_COMMIT" \
 && git -C /src checkout --detach FETCH_HEAD

# Stage 2: minimal runtime. Git and source-control tooling stay out of this image.
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data
RUN apt-get update \
 && apt-get install -y --no-install-recommends bash ca-certificates \
 && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
 && groupadd --gid 1000 augustus \
 && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash augustus \
 && mkdir -p /app /app/static/css /app/static/vendor/@popperjs/core/dist/umd /app/static/vendor/bootstrap/dist/js /opt/volt/templates /data \
 && chown -R augustus:augustus /app /opt/volt /data /home/augustus
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check -r /app/requirements.txt

# Copy only the Volt files used by this lab; retain the original CSS copyright header.
COPY --from=volt-source /src/apps/static/css/volt.css /app/static/css/volt.css
COPY --from=volt-source /src/apps/static/vendor/@popperjs/core/dist/umd/popper.min.js /app/static/vendor/@popperjs/core/dist/umd/popper.min.js
COPY --from=volt-source /src/apps/static/vendor/bootstrap/dist/js/bootstrap.min.js /app/static/vendor/bootstrap/dist/js/bootstrap.min.js
COPY --from=volt-source /src/apps/templates/layouts/base.html /opt/volt/templates/layouts/base.html
COPY --from=volt-source /src/apps/templates/layouts/base-auth.html /opt/volt/templates/layouts/base-auth.html
# Fix the upstream starter's misplaced closing body tag while retaining its Volt layout.
RUN python -c "from pathlib import Path; files=[Path('/opt/volt/templates/layouts/base.html'),Path('/opt/volt/templates/layouts/base-auth.html')]; [(lambda p,s: p.write_text(s.replace('</head>','</head>\\n<body>',1).rsplit('<body>',1)[0]+'</body>'+s.rsplit('<body>',1)[1]))(p,p.read_text()) for p in files]"

COPY app/ /app/
COPY game/ /app/game/
COPY flags/user.txt /home/augustus/user.txt
RUN chmod 0400 /home/augustus/user.txt \
 && chown augustus:augustus /home/augustus/user.txt \
 && chown -R augustus:augustus /app /data
USER augustus
EXPOSE 5000
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/healthz', timeout=3).read()" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "30", "app:app"]
