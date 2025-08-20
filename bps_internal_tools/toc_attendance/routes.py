from flask import render_template, request, redirect, url_for, jsonify
from bps_internal_tools.services.auth import login_required, current_user, tool_required
from . import toc_bp, TOOL_SLUG
from bps_internal_tools.services.queries import search_teacher_by_name, get_courses_for_user, get_students_in_course, get_course_info, search_courses_by_query
from bps_internal_tools.services.sheets import log_attendance
from bps_internal_tools.config import DEFAULT_TERMS

# QUICK PRESETS: label + course_id — add whatever you like
PRESET_COURSES = [
    {"label": "Advisory 10", "course_id": "c003936"},
    {"label": "Composition 11", "course_id": "c004117"},
    {"label": "PHE 7 Red", "course_id": "c004533"},
]


@toc_bp.route("/", methods=["GET"])
@login_required
@tool_required(TOOL_SLUG)
def home():
    # optional landing page for toc feature; could redirect to teacher search
    return redirect(url_for("toc.index"))

@toc_bp.route("/index", methods=["GET", "POST"])
@login_required
@tool_required(TOOL_SLUG)
def index():
    return render_template("index.html",
                           page_title="TOC Attendance",
                           page_subtitle="Simple attendance form for senior school coverage.",
                           active_tool="TOC Attendance",
                           preset_courses=PRESET_COURSES)

@toc_bp.route("/search-teachers")
@login_required
@tool_required(TOOL_SLUG)
def search_teachers():
    from flask import jsonify, request
    q = request.args.get("q", "")
    teachers = search_teacher_by_name(q) if q else []
    return jsonify([{"name": t["full_name"], "id": t["user_id"]} for t in teachers])

@toc_bp.get("/search-courses")
@login_required
@tool_required("toc-attendance")
def search_courses():
    query = (request.args.get("q") or "").strip()
    if not query:
        return jsonify([])

    # Optional: support narrowing by terms from querystring if you want ?terms=BPS_W25,BPS_DP25
    terms_raw = request.args.get("terms")
    terms = [t.strip() for t in terms_raw.split(",")] if terms_raw else None

    results = search_courses_by_query(query, terms=terms, limit=12)
    # frontend expects a simple shape
    return jsonify([
        {
            "id": r["course_id"],
            "name": (r["long_name"] or r["short_name"] or r["course_id"]).strip(),
            "short_name": r["short_name"],
            "long_name": r["long_name"],
            "term_id": r["term_id"],
        } for r in results
    ])

@toc_bp.get("/go")
@login_required
@tool_required("toc-attendance")
def go_direct_course():
    """Utility redirect that lands on the take attendance page given a course_id."""
    course_id = request.args.get("course_id")
    course_name = request.args.get("course_name", "")
    if not course_id:
        return redirect(url_for("toc.index"))
    return redirect(url_for("toc.take_attendance", course_id=course_id, course_name=course_name))

@toc_bp.route("/select_course", methods=["GET","POST"])
@login_required
@tool_required(TOOL_SLUG)
def select_course():
    teacher_id = request.args.get("teacher_id")
    if request.method == "POST":
        course_id = request.form["course_id"]
        return redirect(url_for("toc.take_attendance", course_id=course_id, teacher_id=teacher_id))
    courses = get_courses_for_user(teacher_id, role="teacher", terms=DEFAULT_TERMS)
    return render_template("select_course.html",
                           courses=courses,
                           teacher_id=teacher_id,
                           page_title="TOC Attendance",
                           page_subtitle="Simple attendance form for senior school coverage.",
                           active_tool="TOC Attendance")

@toc_bp.route("/take_attendance/<course_id>", methods=["GET","POST"])
@login_required
@tool_required(TOOL_SLUG)
def take_attendance(course_id):
    students = get_students_in_course(course_id)
    info = get_course_info(course_id) # returns {'short_name':..., 'long_name':...}
    course_name = info.get("long_name") or info.get("short_name") or "Unknown Course"
    teacher_id = request.args.get("teacher_id") # passed via redirect above

    if request.method == "POST":
        absent_ids = request.form.getlist("absent")
        absent_students = [s for s in students if str(s["user_id"]) in absent_ids]
        submitter = current_user().get("display_name") or current_user().get("username")
        log_attendance(absent_students, course_name, submitted_by=submitter)
        return render_template("take_attendance.html",
                               students=students,
                               submitted=True,
                               absent_ids=absent_ids,
                               course_name=course_name,
                               teacher_id=teacher_id,
                               page_title="TOC Attendance",
                               page_subtitle="Simple attendance form for senior school coverage.",
                               active_tool="TOC Attendance")
    return render_template("take_attendance.html",
                           students=students,
                           submitted=False,
                           course_name=course_name,
                           teacher_id=teacher_id,
                           page_title="TOC Attendance",
                           page_subtitle="Simple attendance form for senior school coverage.",
                           active_tool="TOC Attendance")
