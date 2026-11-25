import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from flask import g

LOG_DIR = Path("/app/logs")


@dataclass
class User:
    username: str
    role: int


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def query_db(query, args=(), one=False):
    cursor = g._database.execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    return (rows[0] if rows else None) if one else rows


def try_login(form):
    if not form:
        return None
    username = form.get("username", "")
    password = hash_password(form.get("password", ""))
    result = query_db(
        "SELECT COUNT(*) FROM users WHERE username = ? AND secret = ?",
        (username, password),
        one=True,
    )
    if result and result[0]:
        return {"username": username, "secret": password}
    return None


def get_user(username, secret):
    if isinstance(username, bytes):
        username = username.decode("utf-8")
    if isinstance(secret, bytes):
        secret = secret.decode("utf-8")
    row = query_db(
        "SELECT role FROM users WHERE username = ? AND secret = ?",
        (username, secret),
        one=True,
    )
    if row:
        return User(username=username, role=row[0])
    return None


def log_login(user):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with (LOG_DIR / f"{today}.log").open("a", encoding="utf-8") as log:
        log.write(f"User(username={user.username},role={user.role}) logged\n")


def badword_in_str(data):
    lowered = data.lower()
    return any(word in lowered for word in ("rand", "system", "exec", "date"))
