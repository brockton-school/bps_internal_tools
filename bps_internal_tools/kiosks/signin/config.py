"""Configuration values for the sign-in kiosk."""

SIGN_OUT_REASONS_STAFF = [
    "Medical Appointment",
    "Personal Appointment",
    "Professional Development",
    "Meeting",
    "Other",
]

SIGN_OUT_REASONS_STUDENT = [
    "Medical Appointment",
    "Illness",
    "Family Commitment",
    "Athletics",
    "Other",
]

STUDENT_SIGN_OUT_MESSAGE = "Please remember to sign back in at the office when you return."
STUDENT_SIGN_IN_MESSAGE = "Please head straight to class after signing in."

PERSONNEL_CSV_PATH = "/app/env/personnel.csv"

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
