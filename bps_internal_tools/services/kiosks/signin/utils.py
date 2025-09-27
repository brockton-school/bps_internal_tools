from datetime import datetime, time
from typing import List

import pytz
from sqlalchemy import func

from bps_internal_tools.extensions import db
from bps_internal_tools.models import People

ACTIVE_STATUS = "active"

def format_time(datetime_obj):
    """Formats a datetime object into a 12-hour time string."""
    return datetime_obj.strftime('%I:%M %p')

def get_version_info():
    try:
        # Define the path to the version info file
        version_file_path = "/app/version_info.txt"
        
        # Open and read the file
        with open(version_file_path, "r") as file:
            version_info = file.read().strip()
        
        return version_info
    except FileNotFoundError:
        # Return a default message if the file is not found
        return "Version information not available"

# Function to read grades from the CSV file
def get_grades() -> List[str]:
    """Return a sorted list of distinct grades for active Canvas users."""

    grade_rows = (
        db.session.query(func.trim(People.grade))
        .filter(func.lower(People.status) == ACTIVE_STATUS)
        .filter(People.grade.isnot(None))
        .filter(func.trim(People.grade) != "")
        .distinct()
        .order_by(func.lower(People.grade))
        .all()
    )

    return [row[0] for row in grade_rows]

# Function to get suggestions from the CSV file
def get_personnel_suggestions(query: str, user_type: str, grade: str) -> List[str]:
    """Return a list of matching names for the provided query."""

    if not query:
        return []

    query = query.strip()
    if not query:
        return []

    people_query = db.session.query(People.full_name).filter(
        func.lower(People.status) == ACTIVE_STATUS
    )

    if user_type == "Staff":
        people_query = people_query.filter(
            (People.grade.is_(None)) | (func.trim(People.grade) == "")
        )
    elif user_type == "Student":
        if grade:
            people_query = people_query.filter(func.lower(func.trim(People.grade)) == grade.lower())
        else:
            people_query = people_query.filter(
                People.grade.isnot(None), func.trim(People.grade) != ""
            )
    else:
        # Visitors are entered manually
        return []

    like_pattern = f"%{query.lower()}%"
    results = (
        people_query.filter(func.lower(People.full_name).like(like_pattern))
        .order_by(People.full_name)
        .limit(10)
        .all()
    )

    return [row[0] for row in results]

def get_school_level(full_name: str) -> str:
    """Return the school level suffix for a staff member if available."""

    if not full_name:
        return ""

    person = (
        db.session.query(People.grade)
        .filter(func.lower(People.status) == ACTIVE_STATUS)
        .filter(func.lower(People.full_name) == full_name.lower())
        .first()
    )

    if not person:
        return ""

    grade = (person[0] or "").strip()
    if not grade:
        return ""

    grade_upper = grade.upper()
    if grade_upper in {"JS", "SS"}:
        return f" ({grade_upper})"
    if grade_upper == "ADMIN":
        return " (Admin)"

    return ""


def get_student_names_by_grade(grade: str) -> List[str]:
    """Return a sorted list of active students for the provided grade."""

    if not grade:
        return []

    results = (
        db.session.query(People.full_name)
        .filter(func.lower(People.status) == ACTIVE_STATUS)
        .filter(func.lower(func.trim(People.grade)) == grade.lower())
        .order_by(People.full_name)
        .all()
    )

    return [row[0] for row in results]

# Helper for preventing reason when end of day sign out
def should_ask_reason_and_return_time(user_type):
    # Get the current time in Vancouver
    vancouver_tz = pytz.timezone("America/Vancouver")
    vancouver_time = datetime.now(vancouver_tz).time()
    cutoff_time = time(14, 0)  # 2:00 PM Vancouver time
    if user_type == "Staff" and vancouver_time > cutoff_time:
        return "false"  # Don't ask for reason/return time
    return "true"  # Ask for reason/return time