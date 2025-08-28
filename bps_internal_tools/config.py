import os

# Define the path where LOCAL Excel files will be stored
LOCAL_STORAGE_PATH = "/app/data"  # Adjust to your needs

DEFAULT_TERMS = ['BPS_W25', 'BPS_DP24', 'BPS_DP25']

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
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

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

def get_config(name=None):
    env = name or os.getenv("FLASK_ENV", "dev")
    return {"dev": DevConfig, "prod": ProdConfig}.get(env, DevConfig)