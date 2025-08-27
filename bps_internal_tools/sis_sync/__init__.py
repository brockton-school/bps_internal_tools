from flask import Blueprint

sis_sync_bp = Blueprint("sis_sync", __name__)
TOOL_SLUG = "sis_sync"

from . import routes  # noqa: E402, F401