import csv, os, tempfile, shutil
from functools import wraps
from flask import session, redirect, url_for, request, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash

#USERS_CSV = os.getenv("AUTH_USERS_CSV", "auth_users.csv")  # path to your users file
USERS_CSV = "/app/env/auth_users.csv"

def load_users():
    users = {}
    if not os.path.exists(USERS_CSV):
        return users
    with open(USERS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = (row.get("username") or "").strip().lower()
            if not username:
                continue
            users[username] = {
                "username": username,
                "password_hash": row.get("password_hash", "").strip(),
                "display_name": row.get("display_name", "").strip() or username,
                # support multiple roles via comma (e.g. admin,attendance)
                "roles": [r.strip() for r in (row.get("role") or row.get("roles") or "user").split(",") if r.strip()],
                "active": (row.get("active", "true").strip().lower() != "false"),
            }
    return users

def _atomic_write_rows(fieldnames, rows):
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="users_", suffix=".csv")
    os.close(tmp_fd)
    try:
        with open(tmp_path, "w", newline='', encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        shutil.move(tmp_path, USERS_CSV)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def save_users(users_dict):
    # users_dict is {username: {...}}
    fieldnames = ["username", "password_hash", "display_name", "roles", "active"]
    rows = []
    for u in sorted(users_dict.values(), key=lambda x: x["username"]):
        rows.append({
            "username": u["username"],
            "password_hash": u["password_hash"],
            "display_name": u.get("display_name") or u["username"],
            "roles": ",".join(u.get("roles") or []),
            "active": "true" if u.get("active", True) else "false",
        })
    _atomic_write_rows(fieldnames, rows)


def authenticate(username, password):
    users = load_users()
    user = users.get((username or "").lower())
    if user and user["active"] and check_password_hash(user["password_hash"], password):
        # store minimal session payload
        return {"username": user["username"], "display_name": user["display_name"], "roles": user["roles"]}
    return None

def current_user():
    return session.get("user")

def has_any_role(user, allowed_roles):
    if not user: return False
    if not allowed_roles: return True
    uroles = set((user.get("roles") or []))
    return bool(uroles.intersection(set(allowed_roles)))

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return redirect(url_for("login", next=request.path))
            if not has_any_role(user, roles):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


# --- Admin-facing helpers for Settings ---
def add_user(username, password, display_name, roles, active=True):
    username = username.strip().lower()
    users = load_users()
    if username in users:
        raise ValueError("User already exists")
    users[username] = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "display_name": display_name.strip() or username,
        "roles": [r.strip() for r in roles if r.strip()],
        "active": bool(active),
    }
    save_users(users)

def update_user(username, display_name=None, roles=None, active=None, new_password=None):
    username = username.strip().lower()
    users = load_users()
    if username not in users:
        raise ValueError("User not found")
    if display_name is not None:
        users[username]["display_name"] = display_name.strip() or username
    if roles is not None:
        users[username]["roles"] = [r.strip() for r in roles if r.strip()]
    if active is not None:
        users[username]["active"] = bool(active)
    if new_password:
        users[username]["password_hash"] = generate_password_hash(new_password)
    save_users(users)

def delete_user(username):
    username = username.strip().lower()
    users = load_users()
    if username in users:
        users.pop(username)
        save_users(users)