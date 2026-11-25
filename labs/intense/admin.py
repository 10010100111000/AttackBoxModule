import os
from pathlib import Path

from flask import Blueprint, abort, render_template, request

from utils import User, get_user

admin = Blueprint("admin", __name__, url_prefix="/admin")
LOG_ROOT = Path("/app/logs")


def is_admin(request_object):
    from app import current_session

    session = current_session()
    if not session or "username" not in session or "secret" not in session:
        return False
    user = get_user(session["username"], session["secret"])
    return bool(user and user.role == 1)


def require_admin():
    if not is_admin(request):
        abort(403)


@admin.get("")
@admin.get("/")
def home():
    require_admin()
    return render_template("admin.html", user=User("admin", 1))


@admin.post("/log/view")
def view_log():
    require_admin()
    filename = request.form.get("logfile", "")
    # Deliberately vulnerable path join: no resolved-path boundary is enforced.
    target = os.path.join(str(LOG_ROOT), filename)
    if not os.path.exists(target):
        return f"Can't find {filename}", 404, {"Content-Type": "text/plain; charset=utf-8"}
    with open(target, "r", encoding="utf-8", errors="replace") as source:
        return source.read(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@admin.post("/log/list")
def list_log():
    require_admin()
    logdir = request.form.get("logdir", "")
    target = os.path.join(str(LOG_ROOT), logdir)
    if not os.path.exists(target):
        return f"Can't find {logdir}", 404, {"Content-Type": "text/plain; charset=utf-8"}
    try:
        return "\n".join(os.listdir(target)), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except OSError as error:
        return str(error), 400, {"Content-Type": "text/plain; charset=utf-8"}
