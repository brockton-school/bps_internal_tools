# toc_attendance/__init__.py
from flask import Blueprint, abort
from auth import current_user

toc_bp = Blueprint("toc", __name__)  # you can omit template_folder if using app-level templates
TOOL_SLUG = "toc_attendance"

# IMPORTANT: import routes so the @toc_bp.route decorators execute
from . import routes  # noqa: E402, F401

REQUIRED_ROLES = {"attendance", "admin"}  # who can access this tool
