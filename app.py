from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from auth import authenticate, login_required, current_user, role_allows_tool
from tools_registry import all_tools, tool_link
from config import DEFAULT_TERMS
from utils import get_version_info
from toc_attendance import toc_bp
from admin import admin_bp
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "dev-key")

@app.context_processor
def inject_auth_user():
    # already injecting version info; just add user
    return {"auth_user": current_user()}

@app.context_processor
def inject_footer_info():
    vi = get_version_info()
    github_repo = "https://github.com/brockton-school/bps_internal_tools"
    commit_url = f"{github_repo}/commit/{vi['commit']}" if vi['commit'] != "unknown" else None

    return {
        "version_info": vi['version'],
        "commit_hash": vi['commit'],
        "commit_url": commit_url,
        "copyright_text": "© 2025 Brockton School. All rights reserved."
    }

@app.context_processor
def inject_page_meta():
    return {
        "page_title": "Brockton School Internal Tools",          # default for /
        "page_subtitle": "Choose a tool to begin",
        "active_tool": None                      # None on tools index; set string inside tools
    }

# Register Bluprints
app.register_blueprint(toc_bp, url_prefix="/toc-attendance")
app.register_blueprint(admin_bp, url_prefix="/admin")


# error handling
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/")
@login_required
def tools_index():
    u = current_user()
    tools = []
    for t in all_tools():
        if role_allows_tool(u["role"], t["slug"]):
            tools.append({**t, "url": tool_link(t)})
    return render_template("tools_index.html",
                           tools=tools,
                           page_title="Internal Tools",
                           page_subtitle="Choose a tool to begin",
                           active_tool=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = authenticate(username, password)
        if user:
            session["user"] = user
            nxt = request.args.get("next") or url_for("tools_index")
            return redirect(nxt)
        flash("Invalid username or password.", "error")
    return render_template("login.html", 
                           page_title="Brockton School Internal Tools",
                           page_subtitle="Authentication Required, Please Sign In",
                           active_tool=None)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


print(app.url_map)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

