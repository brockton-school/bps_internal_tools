from flask import Flask, flash, redirect, request, session, url_for


from .config import get_config
from .extensions import db
from .auth import auth_bp
from .admin import admin_bp
from .toc_attendance import toc_bp
from .sis_sync import sis_sync_bp
from .security import set_security_headers
from .extensions import oauth

def create_app(config_name=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(get_config(config_name))
    
    set_security_headers(app)

    # init extensions
    db.init_app(app)

    oauth.init_app(app)
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        client_kwargs={"scope": "openid email profile"},
    )

    # blueprints
    # app.register_blueprint(auth_bp)    # if you split login routes
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(toc_bp, url_prefix="/toc-attendance")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(sis_sync_bp, url_prefix="/sis-sync")

    # error handlers (keep your 403/404)
    from flask import render_template
    @app.errorhandler(403)
    def forbidden(e): return render_template("error/403.html"), 403
    @app.errorhandler(404)
    def not_found(e): return render_template("error/404.html"), 404

    from bps_internal_tools.auth.routes import current_user
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
        version_url = f"{github_repo}/releases/tag/{vi['version']}" if vi.get('version') not in (None, "unknown") else None
        return {
            "version_info": vi.get('version'),
            "version_url": version_url,
            "commit_hash": vi.get('commit'),
            "commit_url": commit_url,
            "copyright_text": "© 2025 Brockton School. All rights reserved."
        }
    
    @app.template_filter("initials")
    def initials(name: str) -> str:
        if not name:
            return ""
        parts = name.split()
        if len(parts) == 1:
            return parts[0][:2].upper()
        return "".join(p[0] for p in parts[:2]).upper()
    
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

    return app