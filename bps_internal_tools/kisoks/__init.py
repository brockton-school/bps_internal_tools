"""Kiosk blueprint for kiosk-based tools such as sign-in."""
from flask import Blueprint

kiosk_bp = Blueprint("kiosk", __name__)

# Import routes so decorators are registered
from . import routes  # noqa: E402,F401