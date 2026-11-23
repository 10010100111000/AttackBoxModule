#!/usr/bin/env python3
"""Minimal original Django ORM exception path, based on Vulhub's CVE-2017-12794 app.py.
No fake XSS template or payload-inspection shortcuts: DEBUG's genuine error page is the sink.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", __name__)
import sys
import json
import secrets
import pathlib
import urllib.parse
from django.conf.urls import url
from django.http import HttpResponse
from django.core.management import execute_from_command_line

SECRET_KEY = pathlib.Path("/run/django/django-secret").read_text(encoding="utf-8").strip()
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = __name__
INSTALLED_APPS = ["django.contrib.sessions", "xss"]
MIDDLEWARE_CLASSES = ["django.contrib.sessions.middleware.SessionMiddleware"]
DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql_psycopg2", "NAME": "lab", "USER": "postgres", "HOST": "127.0.0.1", "PORT": "5432"}}
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": []}]
USE_I18N = False

def home(request):
    return HttpResponse("""<!doctype html><html lang="en"><meta charset="utf-8"><title>Harbor Registry</title><style>body{font:16px system-ui;background:#f4f6f8;color:#26323c}main{margin:10vh auto;max-width:560px;padding:35px;background:white;border:1px solid #dce1e7;border-radius:12px}input,button{padding:10px;margin-top:8px}input{width:72%}button{background:#1c5368;color:white;border:0;border-radius:5px}</style><main><small>HARBOR / PUBLIC REGISTRY</small><h1>Create a community profile</h1><p>Register your public profile handle. Handles must be unique.</p><p><a href="/editorial/">Editorial submissions</a></p><form action="/create_user/" method="get"><label for="username">Public handle</label><br><input id="username" name="username" maxlength="32" required><button>Register</button></form></main></html>""")

def user(request):
    # Intentionally preserves the upstream Vulhub trigger verbatim:
    # PostgreSQL IntegrityError contains the duplicate string, Django's
    # vulnerable technical 500 page renders that error unsafely.
    from xss.models import User
    User.objects.create(username=request.GET['username'])
    return HttpResponse("Registration received.")


def editorial(request):
    """Ordinary public submission queue; vulnerability remains in upstream Django."""
    if request.method == "POST":
        url_text = request.POST.get("website", "")
        parts = urllib.parse.urlsplit(url_text)
        if len(url_text) > 4096 or parts.scheme not in ("http", "https") or not parts.netloc or not parts.path.startswith("/") or parts.path.startswith("//"):
            return HttpResponse("Invalid URL", status=400)
        queue = pathlib.Path("/run/django/reports")
        if len(list(queue.glob("*.json"))) >= 20:
            return HttpResponse("Review queue busy", status=429)
        ticket = secrets.token_hex(16)
        tmp = queue / ("." + ticket + ".tmp")
        tmp.write_text(json.dumps({"website": url_text}), encoding="utf-8")
        tmp.chmod(0o660)
        tmp.rename(queue / (ticket + ".json"))
        return HttpResponse("Editorial link queued.")
    return HttpResponse("""<!doctype html><html><head><meta charset="utf-8"><title>Editorial submissions</title></head><body><main><h1>Share a public profile</h1><p>Editors review community-submitted profile links.</p><form method="post"><label>Website <input type="url" name="website" required></label><button>Submit</button></form></main></body></html>""")

def staff_login(request):
    if request.method == "POST":
        value = request.POST.get("password", "")
        expected = pathlib.Path("/run/django/admin-password").read_text(encoding="utf-8").strip()
        if secrets.compare_digest(value, expected):
            request.session["is_editor"] = True
            return HttpResponse("Editor access granted.")
        return HttpResponse("Invalid credentials", status=403)
    return HttpResponse('<!doctype html><html><body><h1>Editorial login</h1><form method="post"><input type="password" name="password"><button>Sign in</button></form></body></html>')

def staff_flag(request):
    if not request.session.get("is_editor"):
        return HttpResponse("Forbidden", status=403)
    response = HttpResponse(pathlib.Path("/run/django/editorial.flag").read_text(encoding="utf-8"), content_type="text/plain")
    response["Cache-Control"] = "no-store"
    return response

def health(request):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return HttpResponse("ok")

urlpatterns = [
    url(r"^$", home),
    url(r"^create_user/$", user),
    url(r"^healthz$", health),
    url(r"^editorial/$", editorial),
    url(r"^staff/login$", staff_login),
    url(r"^staff/flag$", staff_flag),
]

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
