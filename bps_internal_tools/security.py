# bps_internal_tools/security.py
from flask import request

def set_security_headers(app):
    @app.after_request
    def add_headers(resp):
        # resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        # resp.headers.setdefault("X-Frame-Options", "DENY")
        # resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        # # If you want CSP now (allow your fonts/js):
        # resp.headers.setdefault("Content-Security-Policy",
        #     "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
        #     "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'")
        return resp
