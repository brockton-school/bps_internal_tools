from flask import render_template, request, redirect, url_for, flash
from auth import load_users, load_roles, add_user, update_user, delete_user, add_role, update_role, delete_role, tool_required
from . import admin_bp, TOOL_SLUG

@admin_bp.route("/settings", methods=["GET"])
@tool_required(TOOL_SLUG)
def settings_home():
    return render_template("admin_settings.html",
                           users=sorted(load_users().values(), key=lambda u: u["username"]),
                           roles=sorted(load_roles().values(), key=lambda r: r["role"]),
                           page_title="Admin Settings",
                           page_subtitle="Manage users and roles",
                           active_tool="Settings")

# Roles
@admin_bp.route("/settings/roles/create", methods=["POST"])
@tool_required(TOOL_SLUG)
def create_role():
    name = (request.form.get("role") or "").strip()
    tools_raw = (request.form.get("tools") or "").strip()
    tools = ["*"] if tools_raw == "*" else [t.strip() for t in tools_raw.split(",") if t.strip()]
    active = (request.form.get("active") == "on")
    try:
        add_role(name, tools, active)
        flash(f"Role '{name}' created", "ok")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.settings_home"))

@admin_bp.route("/settings/roles/update/<role>", methods=["POST"])
@tool_required(TOOL_SLUG)
def update_role_route(role):
    tools_raw = (request.form.get("tools") or "").strip()
    tools = ["*"] if tools_raw == "*" else [t.strip() for t in tools_raw.split(",") if t.strip()]
    active = (request.form.get("active") == "on")
    try:
        update_role(role, tools, active)
        flash(f"Role '{role}' updated", "ok")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.settings_home"))

@admin_bp.route("/settings/roles/delete/<role>", methods=["POST"])
@tool_required(TOOL_SLUG)
def delete_role_route(role):
    delete_role(role)
    flash(f"Role '{role}' deleted", "ok")
    return redirect(url_for("admin.settings_home"))

# Users (single-role)
@admin_bp.route("/settings/users/create", methods=["POST"])
@tool_required(TOOL_SLUG)
def create_user_route():
    username = request.form.get("username","").strip()
    display_name = request.form.get("display_name","").strip()
    role = request.form.get("role","user").strip()
    password = request.form.get("password","")
    if not username or not password:
        flash("Username and password are required", "error")
        return redirect(url_for("admin.settings_home"))
    add_user(username, password, display_name, role, active=True)
    flash(f"User '{username}' created", "ok")
    return redirect(url_for("admin.settings_home"))

@admin_bp.route("/settings/users/update/<username>", methods=["POST"])
@tool_required(TOOL_SLUG)
def update_user_route(username):
    display_name = request.form.get("display_name")
    role = request.form.get("role")
    active = (request.form.get("active") == "on")
    new_password = request.form.get("new_password") or None
    update_user(username, display_name, role, active, new_password)
    flash(f"User '{username}' updated", "ok")
    return redirect(url_for("admin.settings_home"))

@admin_bp.route("/settings/users/delete/<username>", methods=["POST"])
@tool_required(TOOL_SLUG)
def delete_user_route(username):
    delete_user(username)
    flash(f"User '{username}' deleted", "ok")
    return redirect(url_for("admin.settings_home"))
