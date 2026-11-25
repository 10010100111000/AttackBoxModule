import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, make_response, redirect, render_template, request, send_file, url_for

from admin import admin
from lwt import InvalidSignature, create_cookie, parse_cookie
from utils import badword_in_str, get_user, log_login, try_login

APP_DIR = Path(__file__).resolve().parent
DATABASE = os.environ.get("INTENSE_DB", "/var/lib/intense/app.db")
SOURCE_ARCHIVE = APP_DIR / "src.zip"

app = Flask(__name__)
app.register_blueprint(admin)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = sqlite3.connect(DATABASE, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout = 5000")
        g._database = db
    return db


@app.teardown_appcontext
def close_connection(_exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def current_session():
    cookie = request.cookies.get("auth")
    if not cookie:
        return None
    try:
        return parse_cookie(cookie)
    except (InvalidSignature, ValueError, TypeError):
        return None


def current_user():
    session = current_session()
    if not session or "username" not in session or "secret" not in session:
        return None
    user = get_user(session["username"], session["secret"])
    if user:
        log_login(user)
    return user


def login_required():
    user = current_user()
    if not user:
        abort(401)
    return user


@app.get("/healthz")
def healthz():
    try:
        get_db().execute("SELECT 1").fetchone()
    except sqlite3.Error:
        abort(503)
    return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/")
@app.get("/home")
def index():
    return render_template("index.html", user=current_user())


@app.get("/src.zip")
def source_archive():
    if not SOURCE_ARCHIVE.is_file():
        abort(404)
    return send_file(SOURCE_ARCHIVE, mimetype="application/zip", as_attachment=True, download_name="src.zip")


@app.get("/login")
def login():
    return render_template("login.html", user=current_user())


@app.post("/postlogin")
def postlogin():
    data = try_login(request.form)
    if not data:
        return "Login failed", 401, {"Content-Type": "text/plain; charset=utf-8"}
    response = make_response("OK")
    response.set_cookie("auth", create_cookie(data), httponly=True, samesite="Lax", path="/")
    return response


@app.get("/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    response.delete_cookie("auth", path="/")
    return response


@app.get("/submit")
def submit():
    user = login_required()
    return render_template("submit.html", user=user)


@app.post("/submitmessage")
def submit_message():
    login_required()
    message = request.form.get("message", "")
    if len(message) > 140:
        return "message too long", 400, {"Content-Type": "text/plain; charset=utf-8"}
    if badword_in_str(message):
        return "forbidden word in message", 400, {"Content-Type": "text/plain; charset=utf-8"}
    # Intentional application-level SQL injection: the real SQLite engine
    # evaluates the interpolated value and returns its native errors.
    try:
        get_db().execute("INSERT INTO messages VALUES ('%s')" % message)
        get_db().commit()
    except sqlite3.Error as error:
        return str(error), 200, {"Content-Type": "text/plain; charset=utf-8"}
    return "OK", 200, {"Content-Type": "text/plain; charset=utf-8"}



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
