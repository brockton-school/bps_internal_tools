"""Routes for kiosk tools."""
from flask import render_template

from . import kiosk_bp


@kiosk_bp.route("/sign-in")
def sign_in():
    """Placeholder route for kiosk sign-in."""
    return render_template(
        "kiosk_sign_in_placeholder.html",
        page_title="Kiosk Sign-In",
        page_subtitle="Work in progress",
    )