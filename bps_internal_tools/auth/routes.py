from flask import Blueprint, redirect, render_template, url_for, request, session, abort, current_app, flash
from sqlalchemy import select, func
import re
from werkzeug.security import check_password_hash

from . import auth_bp

from bps_internal_tools.extensions import db, oauth
from bps_internal_tools.models import User, Role, RoleTool, People  # People = Canvas users table

def current_user():
    return session.get("user")

def _ensure_role(name: str):
    r = db.session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if not r:
        r = Role(name=name, active=True)
        db.session.add(r)
        db.session.commit()
    return r

def _assign_default_role_for_email(local_part: str) -> str:
    return "student_lite" if re.search(r"\d", local_part) else "staff_lite"

def _find_canvas_user_id_by_email(email: str):
    row = db.session.execute(
        select(People.user_id).where(func.lower(People.email) == email.lower())
    ).first()
    return row[0] if row else None

# ---------- Local + Google combined login ----------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, bounce to tools
    if current_user():
        return redirect(url_for("tools_index"))

    next_url = request.args.get("next") or url_for("tools_index")

    if request.method == "POST":
        # ---- Local username/password path ----
        username = (request.form.get("username") or "").strip().lower()
        password = (request.form.get("password") or "")
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("auth/login.html", next_url=next_url)

        u = db.session.execute(
            select(User).where(User.username == username, User.active == True)  # noqa: E712
        ).scalar_one_or_none()

        if not u or not u.password_hash or not check_password_hash(u.password_hash, password):
            flash("Invalid username or password.", "error")
            return render_template("auth/login.html", next_url=next_url)

        # Build session payload (same structure used across the app)
        session["user"] = {
            "username": u.username,
            "display_name": u.display_name,
            "role": u.role_name,
            "canvas_user_id": u.canvas_user_id,
            "auth_provider": u.auth_provider or "local",
        }
        return redirect(next_url)

    # GET: show form + Google button
    return render_template("auth/login.html", next_url=next_url)

@auth_bp.route("/login/google")
def login_google():
    next_url = request.args.get("next") or url_for("tools_index")
    session["post_login_redirect"] = next_url
    redirect_uri = current_app.config["OAUTH_REDIRECT_URI"]
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.google.parse_id_token(token)

    email = (userinfo.get("email") or "").strip().lower()
    email_verified = userinfo.get("email_verified", False)
    allowed = current_app.config.get("ALLOWED_DOMAIN", "brocktonschool.com").lower()

    if not email or not email_verified or not email.endswith(f"@{allowed}"):
        abort(403)

    display_name = userinfo.get("name") or email.split("@", 1)[0]
    local_part = email.split("@", 1)[0]

    # Ensure default roles exist
    _ensure_role("staff_lite")
    _ensure_role("student_lite")
    default_role = _assign_default_role_for_email(local_part)

    # Try to link to Canvas user
    canvas_user_id = _find_canvas_user_id_by_email(email)

    # Upsert users_auth
    u = db.session.execute(select(User).where(User.username == email)).scalar_one_or_none()
    if not u:
        u = User(
            username=email,
            password_hash="",                 # not used for Google
            display_name=display_name,
            role_name=default_role,
            active=True,
            auth_provider="google",
            canvas_user_id=canvas_user_id,
        )
        db.session.add(u)
    else:
        u.display_name = display_name
        u.auth_provider = "google"
        if not u.canvas_user_id and canvas_user_id:
            u.canvas_user_id = canvas_user_id
        if not u.role_name:
            u.role_name = default_role
    db.session.commit()

    session["user"] = {
        "username": u.username,
        "display_name": u.display_name,
        "role": u.role_name,
        "canvas_user_id": u.canvas_user_id,
        "auth_provider": "google",
    }

    dest = session.pop("post_login_redirect", None) or url_for("tools_index")
    return redirect(dest)

@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("tools_index"))