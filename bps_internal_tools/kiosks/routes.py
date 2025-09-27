"""Routes for kiosk tools."""
from flask import redirect, url_for

from . import kiosk_bp


@kiosk_bp.route("/sign-in")
def sign_in():
    """Redirect legacy sign-in path to the kiosk sign-in tool."""
    return redirect(url_for("kiosks_signin.index"))