import os

# Google Sheets configuration
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')

# This is software access logins
PATH_TO_USERS = "/app/env/users.csv"

# This is random secure key for signing session data
# This is used as part of the personnel.csv upload process
# **NOTE** To generate a key `python -c "import secrets; print(secrets.token_hex(16))"`
FLASK_SECRET_KEY = os.getenv('SECRET_KEY')

# Define the path where LOCAL Excel files will be stored
LOCAL_STORAGE_PATH = "/app/data"  # Adjust to your needs

DEFAULT_TERMS = ['BPS_W25', 'BPS_DP24', 'BPS_DP25']
