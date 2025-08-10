import csv, os, tempfile, shutil
from functools import wraps
from flask import session, redirect, url_for, request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import select, delete
from db import SessionLocal
from models import User, Role, RoleTool

HASH_METHOD = "pbkdf2:sha256"

# ---------- Loaders ----------
def load_users():
    with SessionLocal() as s:
        return {u.username: {
            "username": u.username, "display_name": u.display_name,
            "role": u.role_name, "active": u.active
        } for u in s.execute(select(User)).scalars().all()}

def load_roles():
    with SessionLocal() as s:
        roles = {}
        rows = s.execute(select(Role)).scalars().all()
        for r in rows:
            tool_rows = s.execute(select(RoleTool.tool_slug).where(RoleTool.role_id == r.id)).scalars().all()
            roles[r.name] = {"role": r.name, "tools": tool_rows or [], "active": r.active}
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
    with SessionLocal() as s:
        u = s.execute(select(User).where(User.username == username.lower())).scalar_one_or_none()
        if u and u.active and check_password_hash(u.password_hash, password):
            return {"username": u.username, "display_name": u.display_name, "role": u.role_name}
    return None

def current_user():
    return session.get("user")

def role_allows_tool(role_name, tool_slug):
    with SessionLocal() as s:
        role = s.execute(select(Role).where(Role.name == role_name, Role.active == True)).scalar_one_or_none()  # noqa
        if not role: return False
        # admin style: if role has '*' allow all
        any_star = s.execute(select(RoleTool).where(RoleTool.role_id == role.id, RoleTool.tool_slug == "*")).first()
        if any_star: return True
        got = s.execute(select(RoleTool).where(RoleTool.role_id == role.id, RoleTool.tool_slug == tool_slug)).first()
        return bool(got)

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
    with SessionLocal() as s:
        if s.execute(select(User).where(User.username == username.lower())).first():
            raise ValueError("User already exists")
        s.add(User(
            username=username.lower(),
            password_hash=generate_password_hash(password, method=HASH_METHOD),
            display_name=display_name or username,
            role_name=role,
            active=bool(active),
        ))
        s.commit()

def update_user(username, display_name=None, role=None, active=None, new_password=None):
    with SessionLocal() as s:
        u = s.execute(select(User).where(User.username == username.lower())).scalar_one_or_none()
        if not u: raise ValueError("User not found")
        if display_name is not None: u.display_name = display_name or u.username
        if role is not None: u.role_name = role
        if active is not None: u.active = bool(active)
        if new_password: u.password_hash = generate_password_hash(new_password, method=HASH_METHOD)
        s.commit()

def delete_user(username):
    with SessionLocal() as s:
        u = s.execute(select(User).where(User.username == username.lower())).scalar_one_or_none()
        if u:
            s.delete(u)
            s.commit()

def add_role(name, tools, active=True):
    with SessionLocal() as s:
        if s.execute(select(Role).where(Role.name == name)).first():
            raise ValueError("Role already exists")
        r = Role(name=name, active=bool(active))
        s.add(r); s.flush()
        if tools == ["*"]:
            s.add(RoleTool(role_id=r.id, tool_slug="*"))
        else:
            for slug in tools or []:
                s.add(RoleTool(role_id=r.id, tool_slug=slug))
        s.commit()


def update_role(name, tools=None, active=None):
    with SessionLocal() as s:
        r = s.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if not r: raise ValueError("Role not found")
        if active is not None: r.active = bool(active)
        if tools is not None:
            s.execute(delete(RoleTool).where(RoleTool.role_id == r.id))
            if tools == ["*"]:
                s.add(RoleTool(role_id=r.id, tool_slug="*"))
            else:
                for slug in tools:
                    s.add(RoleTool(role_id=r.id, tool_slug=slug))
        s.commit()

def delete_role(name):
    with SessionLocal() as s:
        r = s.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if r:
            s.execute(delete(RoleTool).where(RoleTool.role_id == r.id))
            s.delete(r)
            s.commit()