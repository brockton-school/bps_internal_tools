# toc_attendance/__init__.py
from flask import Blueprint, abort
from auth import current_user, has_any_role

toc_bp = Blueprint("toc", __name__)  # you can omit template_folder if using app-level templates

# IMPORTANT: import routes so the @toc_bp.route decorators execute
from . import routes  # noqa: E402, F401

REQUIRED_ROLES = {"attendance", "admin"}  # who can access this tool

@toc_bp.before_request
def _gate_by_role():
    user = current_user()
    if not user or not has_any_role(user, REQUIRED_ROLES):
        abort(403)