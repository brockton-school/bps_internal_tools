import csv
import os
from functools import wraps
from flask import session, redirect, url_for, request, flash
from werkzeug.security import check_password_hash

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
                "role": row.get("role", "").strip() or "user",
                "active": (row.get("active", "true").strip().lower() != "false"),
            }
    return users

def authenticate(username, password):
    users = load_users()
    user = users.get((username or "").lower())
    if user and user["active"] and check_password_hash(user["password_hash"], password):
        return {"username": user["username"], "display_name": user["display_name"], "role": user["role"]}
    return None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            # remember where we were going
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def current_user():
    return session.get("user")
