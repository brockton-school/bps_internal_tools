from flask import render_template, request, redirect, url_for, flash
from auth import roles_required, load_users, add_user, update_user, delete_user
from . import admin_bp

@admin_bp.route("/settings", methods=["GET"])
@roles_required("admin")
def settings_home():
    users = load_users()
    # sort for display
    table = sorted(users.values(), key=lambda u: (not u["active"], u["username"]))
    return render_template("admin_settings.html",
                           users=table,
                           page_title="Admin Settings",
                           page_subtitle="Manage users and roles",
                           active_tool="Settings")

@admin_bp.route("/settings/create", methods=["POST"])
@roles_required("admin")
def create_user():
    username = request.form.get("username","").strip()
    display_name = request.form.get("display_name","").strip()
    roles = [r.strip() for r in (request.form.get("roles","").split(",") if request.form.get("roles") else [])]
    password = request.form.get("password","")
    if not username or not password:
        flash("Username and password are required", "error")
        return redirect(url_for("admin.settings_home"))
    try:
        add_user(username, password, display_name, roles, active=True)
        flash(f"User '{username}' created", "ok")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.settings_home"))

@admin_bp.route("/settings/update/<username>", methods=["POST"])
@roles_required("admin")
def update_user_route(username):
    display_name = request.form.get("display_name")
    roles = [r.strip() for r in (request.form.get("roles","").split(",") if request.form.get("roles") else [])]
    active = (request.form.get("active") == "on")
    new_password = request.form.get("new_password") or None
    try:
        update_user(username, display_name, roles, active, new_password)
        flash(f"User '{username}' updated", "ok")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.settings_home"))

@admin_bp.route("/settings/delete/<username>", methods=["POST"])
@roles_required("admin")
def delete_user_route(username):
    delete_user(username)
    flash(f"User '{username}' deleted", "ok")
    return redirect(url_for("admin.settings_home"))
