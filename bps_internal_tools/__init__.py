from flask import Flask, flash, redirect, request, session, url_for


from .config import get_config
from .extensions import db
from .admin import admin_bp
from .toc_attendance import toc_bp
from .security import set_security_headers

def create_app(config_name=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(get_config(config_name))
    
    set_security_headers(app)

    # init extensions
    db.init_app(app)

    # blueprints
    # app.register_blueprint(auth_bp)    # if you split login routes
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(toc_bp, url_prefix="/toc-attendance")

    # error handlers (keep your 403/404)
    from flask import render_template
    @app.errorhandler(403)
    def forbidden(e): return render_template("403.html"), 403
    @app.errorhandler(404)
    def not_found(e): return render_template("404.html"), 404

    @app.context_processor
    def inject_auth_user():
        # already injecting version info; just add user
        return {"auth_user": current_user()}

    # context processors (version info, copyright)
    from bps_internal_tools.services.utils import get_version_info
    @app.context_processor
    def inject_footer_info():
        vi = get_version_info()
        github_repo = "https://github.com/brockton-school/bps_internal_tools"
        commit_url = f"{github_repo}/commit/{vi['commit']}" if vi.get('commit') not in (None, "unknown") else None
        return {
            "version_info": vi.get('version'),
            "commit_hash": vi.get('commit'),
            "commit_url": commit_url,
            "copyright_text": "© 2025 Brockton School. All rights reserved."
        }
    
    from sqlalchemy import text
    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok"}, 200
        except Exception as e:
            return {"status": "error", "detail": str(e)}, 500

    from bps_internal_tools.services.auth import authenticate, current_user, login_required, role_allows_tool
    from bps_internal_tools.tools_registry import all_tools, tool_link
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

    return app