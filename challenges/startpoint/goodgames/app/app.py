import hashlib
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from flask import Flask, abort, jsonify, redirect, render_template, render_template_string, request, send_from_directory, session, url_for
from jinja2 import ChoiceLoader, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
GAME_DIR = BASE_DIR / "game" if (BASE_DIR / "game").is_dir() else PROJECT_DIR / "game"
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "goodgames.sqlite3"
ADMIN_HOST = "internal-administration.goodgames.htb"

app = Flask(
    __name__,
    static_folder="/app/static",
    static_url_path="/static",
    template_folder=str(BASE_DIR / "templates"),
)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "goodgames-lab-change-this-secret"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)
# Load our route-specific pages first, then the upstream Volt Flask/Jinja templates.
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(str(BASE_DIR / "templates")),
    FileSystemLoader("/opt/volt/templates"),
])


def current_host():
    return request.host.split(":", 1)[0].lower()


def is_admin_host():
    return current_host() == ADMIN_HOST


def get_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def database():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def md5_hex(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def init_db():
    with database() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )"""
        )
        conn.execute(
            "INSERT OR IGNORE INTO user (username, email, password) VALUES (?, ?, ?)",
            ("admin", "admin@goodgames.htb", md5_hex("superadministrator")),
        )
        conn.execute(
            "INSERT OR IGNORE INTO user (username, email, password) VALUES (?, ?, ?)",
            ("james", "james@goodgames.htb", md5_hex("james123")),
        )


init_db()


@app.get("/healthz")
def healthz():
    try:
        with database() as conn:
            conn.execute("SELECT 1").fetchone()
        return jsonify(status="ok", checks={"web": "ok", "database": "ok"}), 200
    except Exception:
        app.logger.exception("Health check failed")
        return jsonify(status="unhealthy", checks={"web": "ok", "database": "failed"}), 503


@app.get("/")
def index():
    if is_admin_host():
        if session.get("admin_authenticated"):
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("login"))
    return send_from_directory(GAME_DIR, "index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_admin_host():
        if request.method == "GET":
            if session.get("admin_authenticated"):
                return redirect(url_for("admin_dashboard"))
            return render_template("volt/sign-in.html", error=False)

        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "superadministrator":
            session["admin_authenticated"] = True
            session["admin_username"] = "admin"
            return redirect(url_for("admin_dashboard"))
        return render_template("volt/sign-in.html", error=True), 401

    if request.method == "GET":
        return redirect(url_for("index"))

    email = request.form.get("email", "")
    password = request.form.get("password", "")
    # INTENTIONAL LAB VULNERABILITY: email is concatenated into SQL.
    # The password is hashed to reproduce the weak-hash database disclosure path.
    query = (
        "SELECT id, username, email, password FROM user "
        f"WHERE email = '{email}' AND password = '{md5_hex(password)}'"
    )
    try:
        with database() as conn:
            row = conn.execute(query).fetchone()
    except sqlite3.Error:
        row = None

    if row:
        session["main_user"] = row["username"]
        session["main_email"] = row["email"]
        return redirect(url_for("account"))
    return "Invalid email or password", 401


@app.get("/account")
def account():
    if not session.get("main_user"):
        return redirect(url_for("index"))
    return render_template("volt/main-account.html", username=session.get("main_user"))


def require_admin():
    if not is_admin_host():
        abort(404)
    if not session.get("admin_authenticated"):
        return redirect(url_for("login"))
    return None


@app.get("/dashboard")
def admin_dashboard():
    denied = require_admin()
    if denied:
        return denied
    return render_template("volt/dashboard.html", segment="dashboard", parent="pages")


@app.route("/settings", methods=["GET", "POST"])
def admin_settings():
    denied = require_admin()
    if denied:
        return denied

    if request.method == "POST":
        raw_name = request.form.get("name", "")
        with database() as conn:
            conn.execute("UPDATE user SET username = ? WHERE email = ?", (raw_name, "admin@goodgames.htb"))
        return redirect(url_for("admin_settings"))

    with database() as conn:
        row = conn.execute("SELECT username, email FROM user WHERE email = ?", ("admin@goodgames.htb",)).fetchone()
    raw_name = row["username"] if row else "admin"
    # INTENTIONAL LAB VULNERABILITY: stored user input is compiled as a Jinja template.
    rendered_name = render_template_string(raw_name)
    return render_template(
        "volt/settings.html",
        segment="settings",
        parent="pages",
        profile_name=rendered_name,
        profile_email=row["email"] if row else "admin@goodgames.htb",
    )


@app.get("/logout")
def logout():
    session.clear()
    if is_admin_host():
        return redirect(url_for("login"))
    return redirect(url_for("index"))


@app.route("/<path:filename>")
def game_files(filename):
    # The original Game Warrior pages and assets are served unchanged under their paths.
    candidate = (GAME_DIR / filename).resolve()
    if not str(candidate).startswith(str(GAME_DIR.resolve()) + os.sep) or not candidate.is_file():
        abort(404)
    return send_from_directory(GAME_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
