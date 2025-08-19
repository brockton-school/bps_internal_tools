from flask import Blueprint

auth_bp = Blueprint("auth", __name__)  # you can omit template_folder if using app-level templates


# IMPORTANT: import routes so the @toc_bp.route decorators execute
from . import routes  # noqa: E402, F401