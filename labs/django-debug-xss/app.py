#!/usr/bin/env python3
"""Minimal original Django ORM exception path, based on Vulhub's CVE-2017-12794 app.py.
No fake XSS template or payload-inspection shortcuts: DEBUG's genuine error page is the sink.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", __name__)
import sys
from django.conf.urls import url
from django.http import HttpResponse
from django.core.management import execute_from_command_line

SECRET_KEY = "local-educational-django-debug-secret"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = __name__
INSTALLED_APPS = ["xss"]
MIDDLEWARE_CLASSES = []
DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql_psycopg2", "NAME": "lab", "USER": "postgres", "HOST": "127.0.0.1", "PORT": "5432"}}
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": []}]
USE_I18N = False

def home(request):
    return HttpResponse("""<!doctype html><html lang="en"><meta charset="utf-8"><title>Harbor Registry</title><style>body{font:16px system-ui;background:#f4f6f8;color:#26323c}main{margin:10vh auto;max-width:560px;padding:35px;background:white;border:1px solid #dce1e7;border-radius:12px}input,button{padding:10px;margin-top:8px}input{width:72%}button{background:#1c5368;color:white;border:0;border-radius:5px}</style><main><small>HARBOR / PUBLIC REGISTRY</small><h1>Create a community profile</h1><p>Register your public profile handle. Handles must be unique.</p><form action="/create_user/" method="get"><label for="username">Public handle</label><br><input id="username" name="username" maxlength="32" required><button>Register</button></form></main></html>""")

def user(request):
    # Intentionally preserves the upstream Vulhub trigger verbatim:
    # PostgreSQL IntegrityError contains the duplicate string, Django's
    # vulnerable technical 500 page renders that error unsafely.
    from xss.models import User
    User.objects.create(username=request.GET['username'])
    return HttpResponse("Registration received.")

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
]

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
