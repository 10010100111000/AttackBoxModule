"""Dependency-light checks for the deliberately vulnerable lab logic."""
import hashlib
import sqlite3
from jinja2 import Environment

password_hash = hashlib.md5(b"superadministrator").hexdigest()
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE user (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)")
conn.execute("INSERT INTO user VALUES (1, 'admin', 'admin@goodgames.htb', ?)", (password_hash,))
conn.execute("INSERT INTO user VALUES (2, 'james', 'james@goodgames.htb', 'irrelevant')")

# Mirrors the vulnerable login query in app/app.py.
email = "admin@goodgames.htb' OR 1=1 -- -"
query = (
    "SELECT id, username, email, password FROM user "
    f"WHERE email = '{email}' AND password = '{hashlib.md5(b'not-the-password').hexdigest()}'"
)
row = conn.execute(query).fetchone()
assert row and row[1] == "admin", row
assert password_hash == "2b22337f218b2d82dfc3b6f77e7cb8ec"
assert Environment().from_string("{{7*7}}").render() == "49"
print("SQL injection logic: PASS")
print("Seeded weak hash: PASS")
print("Jinja expression evaluation: PASS")
