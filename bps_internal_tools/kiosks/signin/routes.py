from datetime import datetime

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from bps_internal_tools.config import SignInKioskConfig
from bps_internal_tools.services.auth import current_user, role_allows_tool
from bps_internal_tools.services.kiosks.signin.excel import save_to_local_file
from bps_internal_tools.services.kiosks.signin.sheets import get_or_create_sheet
from bps_internal_tools.services.kiosks.signin.utils import (
    should_ask_reason_and_return_time,
)
from bps_internal_tools.services.queries import (
    get_grades,
    get_personnel_suggestions,
    get_school_level,
    get_student_names_by_grade,
)

from bps_internal_tools.services.settings import get_system_tzinfo
from bps_internal_tools.services.utils import format_time, get_version_info

signin_bp = Blueprint("kiosks_signin", __name__)

@signin_bp.before_request
def ensure_kiosk_access():
    user = current_user()
    if not user:
        next_url = request.full_path if request.query_string else request.path
        return redirect(url_for("auth.login", next=next_url))
    if not role_allows_tool(user.get("role"), "kiosks_signin"):
        abort(403)



@signin_bp.route("/")
def index():
    # Get the git information
    version_info = get_version_info()
    if isinstance(version_info, dict):
        version = version_info.get("version") or "unknown"
        commit = version_info.get("commit") or "unknown"
        version_text = f"Version: {version} ({commit})"
    else:
        version_text = str(version_info)
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
        reasons = SignInKioskConfig.SIGN_OUT_REASONS_STUDENT
    else:
        reasons = SignInKioskConfig.SIGN_OUT_REASONS_STAFF

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
    session_user = current_user() or {}
    account = session_user.get("username", "unknown")

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

    # Get current time using the configured system timezone
    system_timezone = get_system_tzinfo()
    current_time = datetime.now(system_timezone)
    current_date = current_time.strftime("%Y-%m-%d")
    current_time_formatted = format_time(current_time)

    sheet_name = current_date

    # Dict for sheet data
    entry = {
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[0]: current_date,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[1]: current_time_formatted,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[2]: name,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[3]: action,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[4]: user_type_classified,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[5]: grade,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[6]: reason,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[7]: return_time,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[8]: visitor_phone,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[9]: visitor_affiliation,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[10]: visitor_vehicle,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[11]: account,
        SignInKioskConfig.COLUMN_HEADERS_ARRAY[12]: "",
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
            sub_message = SignInKioskConfig.STUDENT_SIGN_IN_MESSAGE
        else:
            sub_message = SignInKioskConfig.STUDENT_SIGN_OUT_MESSAGE

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