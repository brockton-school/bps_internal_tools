from datetime import datetime

import pytz
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from bps_internal_tools.kiosks.signin.config import (
    COLUMN_HEADERS_ARRAY,
    PERSONNEL_CSV_PATH,
    SIGN_OUT_REASONS_STAFF,
    SIGN_OUT_REASONS_STUDENT,
    STUDENT_SIGN_IN_MESSAGE,
    STUDENT_SIGN_OUT_MESSAGE,
)
from bps_internal_tools.services.kiosks.signin.excel import save_to_local_file
from bps_internal_tools.services.kiosks.signin.sheets import get_or_create_sheet
from bps_internal_tools.services.kiosks.signin.utils import (
    format_time,
    get_grades,
    get_personnel_suggestions,
    get_school_level,
    get_student_names_by_grade,
    get_version_info,
    should_ask_reason_and_return_time,
)

signin_bp = Blueprint("kiosks_signin", __name__)


@signin_bp.route("/")
def index():
    # Get the git information
    version_text = get_version_info()
    return render_template("kiosks/signin/index.html", version_text=version_text)


@signin_bp.route("/name", methods=["POST"])
def name():
    user_type = request.form["user_type"]
    if user_type == "Student":
        return redirect(url_for("kiosks_signin.grade"))
    return render_template("kiosks/signin/name.html", user_type=user_type)


@signin_bp.route("/grade", methods=["GET", "POST"])
def grade():
    grades = get_grades()
    if request.method == "POST":
        grade_value = request.form["grade"]
        return render_template(
            "kiosks/signin/name.html", user_type="Student", grade=grade_value
        )
    return render_template("kiosks/signin/grade.html", grades=grades)


@signin_bp.route("/signinout", methods=["POST"])
def signinout():
    name = request.form["guest-name"]
    user_type = request.form["user_type"]
    grade = request.form.get("grade", "")

    reasons = []
    if user_type == "Student":
        reasons = SIGN_OUT_REASONS_STUDENT
    else:
        reasons = SIGN_OUT_REASONS_STAFF

    reason_needed = should_ask_reason_and_return_time(user_type)

    return render_template(
        "kiosks/signin/signinout.html",
        name=name,
        user_type=user_type,
        grade=grade,
        reasons=reasons,
        reason_needed=reason_needed,
    )


@signin_bp.route("/submit", methods=["POST"])
def submit():
    auth = request.authorization
    account = "unknown"
    if auth:
        account = auth.username

    action = request.form["action"]
    name = request.form["name"]
    user_type = request.form["user_type"]
    grade = request.form.get("grade", "")

    reason = request.form.get("reason", "")
    other_reason = request.form.get("other_reason", "")
    visitor_reason = request.form.get("visitor-reason", "")
    visitor_affiliation = request.form.get("visitor-affiliation", "")
    visitor_phone = request.form.get("visitor-phone", "")
    visitor_vehicle = request.form.get("visitor-vehicle", "")
    return_time = request.form.get("return_time", "")

    # Get staff classifications (JS/SS/Admin)
    user_type_classified = ""
    if user_type == "Staff":
        user_type_classified = user_type + get_school_level(name)
    else:
        user_type_classified = user_type

    if other_reason:
        reason = other_reason
    elif visitor_reason:
        reason = visitor_reason

    if action == "Signing In":
        return_time = ''

    # Get current time in Vancouver timezone
    vancouver_tz = pytz.timezone("America/Vancouver")
    current_time = datetime.now(vancouver_tz)
    current_date = current_time.strftime("%Y-%m-%d")
    current_time_formatted = format_time(current_time)

    sheet_name = current_date

    # Dict for sheet data
    entry = {
        COLUMN_HEADERS_ARRAY[0]: current_date,
        COLUMN_HEADERS_ARRAY[1]: current_time_formatted,
        COLUMN_HEADERS_ARRAY[2]: name,
        COLUMN_HEADERS_ARRAY[3]: action,
        COLUMN_HEADERS_ARRAY[4]: user_type_classified,
        COLUMN_HEADERS_ARRAY[5]: grade,
        COLUMN_HEADERS_ARRAY[6]: reason,
        COLUMN_HEADERS_ARRAY[7]: return_time,
        COLUMN_HEADERS_ARRAY[8]: visitor_phone,
        COLUMN_HEADERS_ARRAY[9]: visitor_affiliation,
        COLUMN_HEADERS_ARRAY[10]: visitor_vehicle,
        COLUMN_HEADERS_ARRAY[11]: account,
        COLUMN_HEADERS_ARRAY[12]: "",
    }

    # Create or get the sheet and append the row
    worksheet = get_or_create_sheet(sheet_name)
    worksheet.append_row(
        [
            current_date,
            current_time_formatted,
            name,
            action,
            user_type_classified,
            grade,
            reason,
            return_time,
            visitor_phone,
            visitor_affiliation,
            visitor_vehicle,
            account,
            "",
        ]
    )

    # Save a local copy of data to XLSX doc
    save_to_local_file(entry)

    # Render the confirmation page after submission
    action_text = "Signed In" if action == "Signing In" else "Signed Out"
    confirmation_text = ""
    if user_type == "Visitor" and action == "Signing In":
        confirmation_text = "Sign in successful, please report to the front office."
    else:
        confirmation_text = name + " Has Successfully " + action_text + "!"

    # Set student reminders
    sub_message = ""
    if user_type == "Student":
        if action == "Signing In":
            sub_message = STUDENT_SIGN_IN_MESSAGE
        else:
            sub_message = STUDENT_SIGN_OUT_MESSAGE

    return render_template(
        "kiosks/signin/confirmation.html",
        confirmation_text=confirmation_text,
        sub_message=sub_message,
    )


# Auto complete API calls
@signin_bp.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query", "")
    user_type = request.args.get("user_type", "")
    grade = request.args.get("grade", "")

    # Fetch suggestions based on user type and grade
    suggestions = get_personnel_suggestions(query, user_type, grade)
    return jsonify(suggestions)


@signin_bp.route("/student_names", methods=["GET"])
def student_names():
    grade = request.args.get("grade", "")

    students = get_student_names_by_grade(grade)

    return jsonify(students)


@signin_bp.route("/config")
def config():
    """Render the configuration page."""
    return render_template("kiosks/signin/config.html")


@signin_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    """Handle CSV file upload and overwrite the existing personnel.csv."""
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("kiosks_signin.config"))

    file = request.files["file"]

    if file.filename == "" or not file.filename.endswith(".csv"):
        flash("Invalid file selected. Please upload a .csv file.")
        return redirect(url_for("kiosks_signin.config"))

    file.save(PERSONNEL_CSV_PATH)
    flash("Personnel CSV uploaded successfully and overwritten.")

    return redirect(url_for("kiosks_signin.config"))