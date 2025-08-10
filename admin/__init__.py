from flask import Blueprint
admin_bp = Blueprint("admin", __name__, template_folder="../templates")
TOOL_SLUG = "admin"


# IMPORTANT: import routes so the @toc_bp.route decorators execute
from . import routes  # noqa: E402, F401