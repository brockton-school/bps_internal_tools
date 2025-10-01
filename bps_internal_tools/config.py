import os

# Define the path where LOCAL Excel files will be stored
LOCAL_STORAGE_PATH = "/app/data"  # Adjust to your needs

DEFAULT_TERMS = ['BPS_W25', 'BPS_DP24', 'BPS_DP25']

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    TOC_GOOGLE_SHEET_ID = os.getenv('TOC_GOOGLE_SHEET_ID')
    SIGNIN_GOOGLE_SHEET_ID = os.getenv('SIGNIN_GOOGLE_SHEET_ID')
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")  # https://.../auth/google/callback
    ALLOWED_DOMAIN = os.getenv("ALLOWED_DOMAIN", "brocktonschool.com")
    CANVAS_API_URL = os.getenv("CANVAS_API_URL")
    CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
    CANVAS_ACCOUNT_ID = os.getenv("CANVAS_ACCOUNT_ID", "1")

class SignInKioskConfig:
    """Configuration constants used exclusively by the sign-in kiosk."""

    # Define preset options for the "reason"
    SIGN_OUT_REASONS_STAFF = [
        "Lunch",
        "Sick",
        "Appointment",
        "Meeting",
        "Field Trip",
        "Going Home",
    ]
    SIGN_OUT_REASONS_STUDENT = ["Lunch", "Sick", "Appointment"]

    # Reminders shown to students on confirmation
    STUDENT_SIGN_OUT_MESSAGE = (
        "Your parent must contact the school for illness or appointment related departures."
    )
    STUDENT_SIGN_IN_MESSAGE = (
        "Please remember to collect your Late Slip, if late for class."
    )

    COLUMN_HEADERS_ARRAY = [
        "Date",
        "Time",
        "Name",
        "Action",
        "User Type",
        "Grade",
        "Reason",
        "Return Time",
        "Visitor Phone",
        "Visitor Affiliation",
        "Visitor Vehicle",
        "Recorded By",
        "Check",
    ]

    COLUMN_DATE = 0
    COLUMN_TIME = 1
    COLUMN_NAME = 2
    COLUMN_ACTION = 3
    COLUMN_USER_TYPE = 4
    COLUMN_GRADE = 5
    COLUMN_REASON = 6
    COLUMN_RETURN_TIME = 7
    COLUMN_PHONE = 8

    COLUMN_CHECK = len(COLUMN_HEADERS_ARRAY) - 1
    COLUMNS_TOTAL_INT = len(COLUMN_HEADERS_ARRAY)
    COLUMNS_TOTAL = str(COLUMNS_TOTAL_INT)


class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

def get_config(name=None):
    env = name or os.getenv("FLASK_ENV", "dev")
    return {"dev": DevConfig, "prod": ProdConfig}.get(env, DevConfig)