import hashlib
import os
import secrets
import sqlite3
from pathlib import Path

database = Path(os.environ.get("INTENSE_DB", "/var/lib/intense/app.db"))
database.parent.mkdir(parents=True, exist_ok=True)
connection = sqlite3.connect(database)
try:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            secret TEXT NOT NULL,
            role INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            message TEXT NOT NULL
        );
        """
    )
    count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        guest_secret = hashlib.sha256(b"guest").hexdigest()
        admin_secret = secrets.token_hex(32)
        connection.executemany(
            "INSERT INTO users(username, secret, role) VALUES (?, ?, ?)",
            [("guest", guest_secret, 0), ("admin", admin_secret, 1)],
        )
    connection.commit()
finally:
    connection.close()
