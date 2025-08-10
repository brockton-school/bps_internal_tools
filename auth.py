import csv, os, tempfile, shutil
from functools import wraps
from flask import session, redirect, url_for, request, abort
from werkzeug.security import check_password_hash, generate_password_hash

#USERS_CSV = os.getenv("AUTH_USERS_CSV", "auth_users.csv")  # path to your users file
USERS_CSV = "/app/env/auth_users.csv"
ROLES_CSV = "/app/env/auth_roles.csv"

# ---------- Loaders ----------
def load_users():
    users = {}
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                u = (row.get("username") or "").strip().lower()
                if not u: continue
                users[u] = {
                    "username": u,
                    "password_hash": (row.get("password_hash") or "").strip(),
                    "display_name": (row.get("display_name") or u).strip(),
                    "role": (row.get("role") or "user").strip(),
                    "active": (row.get("active","true").strip().lower() != "false"),
                }
    return users

def load_roles():
    roles = {}
    if os.path.exists(ROLES_CSV):
        with open(ROLES_CSV, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                name = (row.get("role") or "").strip()
                if not name: continue
                tools_raw = (row.get("tools") or "").strip()
                tools = ["*"] if tools_raw == "*" else [t.strip() for t in tools_raw.split(",") if t.strip()]
                roles[name] = {
                    "role": name,
                    "tools": tools,
                    "active": (row.get("active","true").strip().lower() != "false"),
                }
    return roles


# ---------- Saves (atomic) ----------

def _atomic_write(path, fieldnames, rows):
    import tempfile, shutil
    fd, tmp = tempfile.mkstemp(prefix="rbac_", suffix=".csv")
    os.close(fd)
    try:
        with open(tmp, "w", newline='', encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows: w.writerow(r)
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

def save_users(users):
    rows = []
    for u in sorted(users.values(), key=lambda x: x["username"]):
        rows.append({
            "username": u["username"],
            "password_hash": u["password_hash"],
            "display_name": u.get("display_name") or u["username"],
            "role": u.get("role") or "user",
            "active": "true" if u.get("active", True) else "false",
        })
    _atomic_write(USERS_CSV, ["username","password_hash","display_name","role","active"], rows)

def save_roles(roles):
    rows = []
    for r in sorted(roles.values(), key=lambda x: x["role"]):
        tools = "*" if (r.get("tools")==["*"]) else ",".join(r.get("tools") or [])
        rows.append({
            "role": r["role"],
            "tools": tools,
            "active": "true" if r.get("active", True) else "false",
        })
    _atomic_write(ROLES_CSV, ["role","tools","active"], rows)


# ---------- Session / checks ----------

def authenticate(username, password):
    users = load_users()
    u = users.get((username or "").lower())
    if u and u["active"] and check_password_hash(u["password_hash"], password):
        return {"username": u["username"], "display_name": u["display_name"], "role": u["role"]}
    return None

def current_user():
    return session.get("user")

def role_allows_tool(role_name, tool_slug):
    roles = load_roles()
    role = roles.get(role_name)
    if not role or not role["active"]:
        return False
    tools = role.get("tools") or []
    return ("*" in tools) or (tool_slug in tools)

def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("user"):
            return redirect(url_for("login", next=request.path))
        return view(*a, **kw)
    return wrapped

def tool_required(tool_slug):
    def deco(view):
        @wraps(view)
        def wrapped(*a, **kw):
            u = current_user()
            if not u:
                return redirect(url_for("login", next=request.path))
            if not role_allows_tool(u.get("role"), tool_slug):
                abort(403)
            return view(*a, **kw)
        return wrapped
    return deco

# ---------- Admin CRUD ----------
def add_user(username, password, display_name, role, active=True):
    username = username.strip().lower()
    users = load_users()
    if username in users:
        raise ValueError("User already exists")
    users[username] = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "display_name": display_name.strip() or username,
        "role": role.strip() or "user",
        "active": bool(active),
    }
    save_users(users)

def update_user(username, display_name=None, role=None, active=None, new_password=None):
    username = username.strip().lower()
    users = load_users()
    if username not in users:
        raise ValueError("User not found")
    if display_name is not None:
        users[username]["display_name"] = display_name.strip() or username
    if role is not None:
        users[username]["role"] = role.strip() or "user"
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

def add_role(name, tools, active=True):
    roles = load_roles()
    if name in roles:
        raise ValueError("Role already exists")
    roles[name] = {"role": name, "tools": (["*"] if tools==["*"] else tools), "active": bool(active)}
    save_roles(roles)

def update_role(name, tools=None, active=None):
    roles = load_roles()
    if name not in roles:
        raise ValueError("Role not found")
    if tools is not None:
        roles[name]["tools"] = (["*"] if tools==["*"] else tools)
    if active is not None:
        roles[name]["active"] = bool(active)
    save_roles(roles)

def delete_role(name):
    roles = load_roles()
    if name in roles:
        roles.pop(name)
        save_roles(roles)