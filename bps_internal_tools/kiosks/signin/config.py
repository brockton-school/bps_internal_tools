"""Configuration values for the sign-in kiosk."""

# Define preset options for the "reason"
SIGN_OUT_REASONS_STAFF      = ["Lunch", "Sick", "Appointment", "Meeting", "Field Trip", "Going Home"]
SIGN_OUT_REASONS_STUDENT    = ["Lunch", "Sick", "Appointment"]
# Remember to send parent contact to school for sick, or appointment

# Reminders shown to students on confirmation
STUDENT_SIGN_OUT_MESSAGE = "Your parent must contact the school for illness or appointment related departures."
STUDENT_SIGN_IN_MESSAGE = "Please remember to collect your Late Slip, if late for class."

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
