#!/usr/bin/env python3
"""Credential Gate: intentionally vulnerable SQL authentication in a real app.

This lab is deliberately insecure. Run only on an isolated training network.
"""
import csv
import hashlib
import html
import io
import json
import os
import secrets
import sqlite3
import threading
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DB_PATH", "/var/lib/credential-gate/operations.sqlite3"))
FLAG_PATH = Path(os.environ.get("FLAG_PATH", "/opt/credential-gate/flag.txt"))
SESSIONS = {}
SESSIONS_LOCK = threading.Lock()


def connect():
    db = sqlite3.connect(str(DB_PATH), timeout=5)
    db.row_factory = sqlite3.Row
    return db


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS operators (
          id INTEGER PRIMARY KEY,
          username TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          display_name TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('admin', 'analyst', 'viewer'))
        );
        CREATE TABLE IF NOT EXISTS dispatches (
          id INTEGER PRIMARY KEY,
          reference TEXT UNIQUE NOT NULL,
          route TEXT NOT NULL,
          status TEXT NOT NULL,
          classification TEXT NOT NULL,
          summary TEXT NOT NULL
        );
        """)
        if db.execute("SELECT COUNT(*) FROM operators").fetchone()[0] == 0:
            # Each new container gets unknown credentials. The lesson is SQLi,
            # not guessing a hard-coded password from a public repository.
            accounts = [
                ("admin", "A. Morgan", "admin"),
                ("analyst", "T. Chen", "analyst"),
                ("viewer", "N. Singh", "viewer"),
            ]
            for username, display_name, role in accounts:
                digest = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
                db.execute("INSERT INTO operators(username,password_hash,display_name,role) VALUES(?,?,?,?)", (username, digest, display_name, role))
        if db.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0] == 0:
            db.executemany("INSERT INTO dispatches(reference,route,status,classification,summary) VALUES(?,?,?,?,?)", [
                ("OPS-2401", "North Terminal", "Closed", "Internal", "Carrier handover reconciled"),
                ("OPS-2402", "East Dock", "Review", "Internal", "Manifest mismatch pending operator review"),
                ("OPS-2403", "Central Hub", "Closed", "Internal", "Inventory variance investigated"),
                ("OPS-2404", "North Terminal", "Restricted", "Restricted", "Quarterly control export for administrator approval"),
            ])


def escape(value):
    return html.escape(str(value), quote=True)


def page(title, content, user=None):
    if user:
        account = escape(user["display_name"])
        navigation = f'<a href="/dashboard">Overview</a><a href="/reports">Reports</a><form action="/logout" method="post"><button class="linklike" type="submit">Log out</button></form><span class="user">{account}</span>'
    else:
        navigation = '<a href="/">Status</a><a class="nav-login" href="/login">Operator sign in</a>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Northstar Dispatch</title><link rel="stylesheet" href="/static/site.css"></head><body>
    <header class="topbar"><div class="brand"><span class="brandmark">N<span class="square">/</span></span><span>NORTHSTAR <small>DISPATCH</small></span></div><nav>{navigation}</nav></header>
    <main class="shell">{content}</main><footer><span>Northstar Dispatch / Operations Console</span><span>Internal training environment</span></footer>
    </body></html>'''.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthstarConsole"
    sys_version = ""

    def respond(self, status, body, content_type="text/html; charset=utf-8", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        if extra:
            for name, value in extra.items():
                self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location, cookie=None):
        headers = {"Location": location}
        if cookie is not None:
            headers["Set-Cookie"] = cookie
        self.respond(303, b"", extra=headers)

    def current_user(self):
        jar = cookies.SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
            token = jar["sid"].value if "sid" in jar else ""
        except cookies.CookieError:
            return None
        if not token:
            return None
        with SESSIONS_LOCK:
            stored = SESSIONS.get(token)
            if stored and stored[1] < time.time():
                SESSIONS.pop(token, None)
                stored = None
        if not stored:
            return None
        with connect() as db:
            return db.execute("SELECT id,username,display_name,role FROM operators WHERE id=?", (stored[0],)).fetchone()

    def forbidden(self, user=None):
        self.respond(403, page("Access denied", '<div class="panel narrow"><p class="eyebrow">ACCESS CONTROL</p><h1>Administrator access required.</h1><p class="muted">Your session cannot view restricted dispatch exports.</p><a class="btn" href="/dashboard">Return to overview</a></div>', user))

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == "/static/site.css":
            css = (HERE / "static" / "site.css").read_bytes()
            return self.respond(200, css, "text/css; charset=utf-8")
        if route == "/healthz":
            with connect() as db:
                db.execute("SELECT 1").fetchone()
            okay = FLAG_PATH.is_file()
            data = json.dumps({"status": "ok" if okay else "error", "database": "ok", "flag": "present" if okay else "missing"}).encode()
            return self.respond(200 if okay else 503, data, "application/json")
        user = self.current_user()
        if route == "/":
            content = '''<section class="hero"><p class="eyebrow">OPERATIONS / NORTH TERMINAL</p><h1>Every movement,<br><em>accounted for.</em></h1><p class="subtext">Northstar Dispatch coordinates shipment exceptions, route approvals and compliance exports across regional hubs.</p><a class="btn" href="/login">Enter operations console <span aria-hidden="true">→</span></a></section>
            <section class="stats"><article><span>ACTIVE ROUTES</span><strong>08</strong></article><article><span>ON-TIME ARRIVALS</span><strong>98.4%</strong></article><article><span>PENDING REVIEWS</span><strong>01</strong></article></section>
            <section class="panel"><p class="eyebrow">SERVICE NOTICE</p><h2>Operator authentication</h2><p class="muted">Only authorized dispatch staff can access historical reports and restricted control exports. Contact your shift lead for an operator account.</p></section>'''
            return self.respond(200, page("Operations", content, user))
        if route == "/login":
            if user:
                return self.redirect("/dashboard")
            return self.show_login()
        if route in ("/dashboard", "/reports", "/reports/export.csv") and not user:
            return self.redirect("/login")
        if route == "/dashboard":
            with connect() as db:
                records = db.execute("SELECT reference,route,status FROM dispatches ORDER BY id DESC LIMIT 3").fetchall()
            rows = "".join(f'<tr><td>{escape(r["reference"])}</td><td>{escape(r["route"])}</td><td><span class="state">{escape(r["status"])}</span></td></tr>' for r in records)
            content = f'''<p class="eyebrow">SIGNED IN / {escape(user["role"].upper())}</p><h1>Operations overview</h1><p class="subtext">Welcome back, {escape(user["display_name"])}. Review the current exception queue before exporting audit records.</p>
            <div class="columns"><article class="metric"><span>Open exceptions</span><strong>01</strong><small>1 awaiting administrator review</small></article><article class="metric"><span>Latest synchronization</span><strong>09:40</strong><small>Regional dispatch feed</small></article></div>
            <section class="panel"><div class="panel-heading"><div><p class="eyebrow">OPERATIONS DATA</p><h2>Recent dispatches</h2></div><a href="/reports">View reports →</a></div><div class="tablewrap"><table><thead><tr><th>Reference</th><th>Route</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''
            return self.respond(200, page("Overview", content, user))
        if route == "/reports":
            if user["role"] != "admin":
                return self.forbidden(user)
            with connect() as db:
                records = db.execute("SELECT reference,route,status,classification,summary FROM dispatches ORDER BY id").fetchall()
            rows = "".join(f'<tr><td>{escape(r["reference"])}</td><td>{escape(r["route"])}</td><td>{escape(r["classification"])}</td><td><span class="state">{escape(r["status"])}</span></td></tr>' for r in records)
            content = f'''<p class="eyebrow">ADMIN / COMPLIANCE</p><h1>Audit reports</h1><p class="subtext">Control exports include restricted verification markers and must only be handled by authorized administrators.</p><section class="panel"><div class="panel-heading"><div><p class="eyebrow">QUARTERLY REVIEW</p><h2>Manifest exceptions</h2></div><a class="btn compact" href="/reports/export.csv">Export control report ↓</a></div><div class="tablewrap"><table><thead><tr><th>Reference</th><th>Route</th><th>Access class</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''
            return self.respond(200, page("Audit reports", content, user))
        if route == "/reports/export.csv":
            if user["role"] != "admin":
                return self.forbidden(user)
            with connect() as db:
                records = db.execute("SELECT reference,route,classification,summary FROM dispatches ORDER BY id").fetchall()
            content = io.StringIO()
            writer = csv.writer(content)
            writer.writerow(["reference", "route", "classification", "summary", "verification_marker"])
            for r in records:
                marker = FLAG_PATH.read_text(encoding="utf-8").strip() if r["classification"] == "Restricted" else ""
                writer.writerow([r["reference"], r["route"], r["classification"], r["summary"], marker])
            payload = content.getvalue().encode("utf-8")
            return self.respond(200, payload, "text/csv; charset=utf-8", {"Content-Disposition": 'attachment; filename="northstar-audit.csv"'})
        return self.respond(404, page("Not found", '<div class="panel narrow"><h1>Not found</h1><p class="muted">The requested page does not exist.</p></div>', user))

    def show_login(self, error=False):
        notice = '<div class="notice" role="alert">Account ID or password was not accepted.</div>' if error else ''
        content = f'''<section class="loginbox"><div class="loginintro"><p class="eyebrow">STAFF ACCESS / SECURE AREA</p><h1>Operator sign in</h1><p class="subtext">Access route history, compliance reports and restricted audit exports.</p><div class="signin-info"><span class="dot"></span> All regional systems operational</div></div><form class="loginform" method="post" action="/login"><p class="eyebrow">OPERATOR CREDENTIALS</p>{notice}<label for="username">Account ID</label><input id="username" name="username" autocomplete="username" placeholder="Enter account ID" required maxlength="200"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" placeholder="Enter password" required maxlength="200"><button class="btn wide" type="submit">Continue to console →</button><p class="hint">Access is logged for operational review.</p></form></section>'''
        self.respond(401 if error else 200, page("Operator sign in", content))

    def do_POST(self):
        route = urlsplit(self.path).path
        if route == "/logout":
            jar = cookies.SimpleCookie()
            try:
                jar.load(self.headers.get("Cookie", ""))
                token = jar["sid"].value if "sid" in jar else ""
            except cookies.CookieError:
                token = ""
            with SESSIONS_LOCK:
                SESSIONS.pop(token, None)
            return self.redirect("/", "sid=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")
        if route != "/login":
            return self.respond(404, b"not found", "text/plain")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.respond(400, b"invalid request", "text/plain")
        if length <= 0 or length > 8192:
            return self.respond(413, b"invalid request size", "text/plain")
        data = parse_qs(self.rfile.read(length).decode("utf-8", "replace"), keep_blank_values=True)
        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]
        if len(username) > 200 or len(password) > 200:
            return self.show_login(error=True)
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        # INTENTIONAL VULNERABILITY: legacy authentication query concatenates
        # an untrusted username into SQL. Password comparison is in the same
        # statement, so a SQL comment can remove the password requirement.
        # Never use this pattern in a real authentication system.
        query = (
            "SELECT id, username, display_name, role FROM operators "
            f"WHERE username = '{username}' AND password_hash = '{digest}' LIMIT 1"
        )
        try:
            with connect() as db:
                user = db.execute(query).fetchone()
        except sqlite3.Error:
            return self.show_login(error=True)
        if not user:
            return self.show_login(error=True)
        token = secrets.token_urlsafe(32)
        with SESSIONS_LOCK:
            SESSIONS[token] = (user["id"], time.time() + 3600)
        return self.redirect("/dashboard", f"sid={token}; HttpOnly; SameSite=Lax; Path=/")


def main():
    initialize()
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Northstar Dispatch training service listening on {port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
