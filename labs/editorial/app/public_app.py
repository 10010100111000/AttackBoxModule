"""Public publishing site: an intentionally vulnerable SSRF cover preview."""
from __future__ import annotations
import uuid
import urllib.parse
import urllib.request
from pathlib import Path
from flask import Flask, request, render_template, Response

app = Flask(__name__, template_folder="/opt/editorial/templates", static_folder="/opt/editorial/static")
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
UPLOADS = Path("/var/www/editorial/uploads")
FALLBACK = "/static/cover-placeholder.svg"

@app.get("/")
def home():
    return render_template("home.html")

@app.get("/about")
def about():
    return render_template("about.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        return render_template("upload.html", sent=True)
    return render_template("upload.html", sent=False)

@app.post("/upload-cover")
def upload_cover():
    address = request.form.get("bookurl", "").strip()
    file = request.files.get("bookfile")
    content = None
    if address:
        parsed = urllib.parse.urlsplit(address)
        if parsed.scheme in ("http", "https"):
            try:
                # Deliberately does not reject loopback/private addresses.
                # This is a REAL outbound HTTP request by the public web service.
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                with opener.open(address, timeout=2.5) as response:
                    content = response.read(256 * 1024 + 1)
            except (OSError, ValueError, TimeoutError):
                pass
    elif file and file.filename:
        content = file.read(256 * 1024 + 1)
    if not content or len(content) > 256 * 1024:
        return Response(FALLBACK, mimetype="text/plain")
    name = uuid.uuid4().hex
    (UPLOADS / name).write_bytes(content)
    return Response("/static/uploads/" + name, mimetype="text/plain")

@app.get("/healthz")
def health():
    return {"status": "ok"}
