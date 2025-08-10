from flask import render_template, request, redirect, url_for, flash
from auth import load_users, load_roles, add_user, update_user, delete_user, add_role, update_role, delete_role, tool_required
from tools_registry import all_tools, tool_slugs
from . import admin_bp, TOOL_SLUG

@admin_bp.route("/settings", methods=["GET"])
@tool_required(TOOL_SLUG)
def settings_home():
    users = load_users()
    roles = load_roles()
    return render_template(
        "admin_settings_home.html",
        stats={
            "user_count": len(users),
            "active_users": sum(1 for u in users.values() if u["active"]),
            "role_count": len(roles),
            "active_roles": sum(1 for r in roles.values() if r["active"]),
        },
        page_title="Admin · Settings",
        page_subtitle="Manage platform settings",
        active_tool="Settings"
    )


# --- Roles page ---
@admin_bp.route("/settings/roles", methods=["GET"])
@tool_required(TOOL_SLUG)
def roles_page():
    roles = sorted(load_roles().values(), key=lambda r: r["role"])
    tools = all_tools()
    return render_template("admin_roles.html",
                           roles=roles, tools=tools,
                           page_title="Admin · Roles",
                           page_subtitle="Define which tools each role can access",
                           active_tool="Settings")

@admin_bp.route("/settings/roles/create", methods=["POST"])
@tool_required(TOOL_SLUG)
def create_role():
    name = (request.form.get("role") or "").strip()
    # Checkbox list => many values
    selected = request.form.getlist("tools[]")  # e.g., ["toc_attendance", ...] or may be ["*"]
    active = (request.form.get("active") == "on")
    if not name:
        flash("Role name is required", "error"); return redirect(url_for("admin.roles_page"))
    # Validate tools: allow "*" or slugs from registry
    valid_slugs = set(tool_slugs())
    if selected == ["*"]:
        tools = ["*"]
    else:
        tools = [s for s in selected if s in valid_slugs]
    add_role(name, tools, active)
    flash(f"Role '{name}' created", "ok")
    return redirect(url_for("admin.roles_page"))

@admin_bp.route("/settings/roles/update/<role>", methods=["POST"])
@tool_required(TOOL_SLUG)
def update_role_route(role):
    selected = request.form.getlist("tools[]")
    active = (request.form.get("active") == "on")
    valid_slugs = set(tool_slugs())
    tools = ["*"] if selected == ["*"] else [s for s in selected if s in valid_slugs]
    update_role(role, tools, active)
    flash(f"Role '{role}' updated", "ok")
    return redirect(url_for("admin.roles_page"))

@admin_bp.route("/settings/roles/delete/<role>", methods=["POST"])
@tool_required(TOOL_SLUG)
def delete_role_route(role):
    delete_role(role)
    flash(f"Role '{role}' deleted", "ok")
    return redirect(url_for("admin.roles_page"))

# --- Users page ---
@admin_bp.route("/settings/users", methods=["GET"])
@tool_required(TOOL_SLUG)
def users_page():
    users = sorted(load_users().values(), key=lambda u: u["username"])
    roles = sorted(load_roles().values(), key=lambda r: r["role"])
    return render_template("admin_users.html",
                           users=users, roles=roles,
                           page_title="Admin · Users",
                           page_subtitle="Create users and assign roles",
                           active_tool="Settings")

@admin_bp.route("/settings/users/create", methods=["POST"])
@tool_required(TOOL_SLUG)
def create_user_route():
    username = (request.form.get("username") or "").strip()
    display_name = (request.form.get("display_name") or "").strip()
    role = (request.form.get("role") or "user").strip()
    password = request.form.get("password") or ""
    if not username or not password:
        flash("Username and password are required", "error"); return redirect(url_for("admin.users_page"))
    add_user(username, password, display_name, role, active=True)
    flash(f"User '{username}' created", "ok")
    return redirect(url_for("admin.users_page"))

@admin_bp.route("/settings/users/update/<username>", methods=["POST"])
@tool_required(TOOL_SLUG)
def update_user_route(username):
    display_name = request.form.get("display_name")
    role = request.form.get("role")
    active = (request.form.get("active") == "on")
    new_password = request.form.get("new_password") or None
    update_user(username, display_name, role, active, new_password)
    flash(f"User '{username}' updated", "ok")
    return redirect(url_for("admin.users_page"))

@admin_bp.route("/settings/users/delete/<username>", methods=["POST"])
@tool_required(TOOL_SLUG)
def delete_user_route(username):
    delete_user(username)
    flash(f"User '{username}' deleted", "ok")
    return redirect(url_for("admin.users_page"))