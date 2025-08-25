from flask import render_template, request, redirect, url_for
from bps_internal_tools.services.auth import login_required, current_user, tool_required
from . import toc_bp, TOOL_SLUG
from bps_internal_tools.services.queries import (
    search_teacher_by_name,
    get_courses_for_user,
    get_students_in_course,
    get_students_in_grade_section,
    get_teachers_in_course,
    get_course_info,
    get_grade_sections,
    get_grade_section
)
from bps_internal_tools.services.sheets import log_attendance
from bps_internal_tools.config import DEFAULT_TERMS


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
    grade_sections = get_grade_sections()
    print(grade_sections)
    return render_template(
        "index.html",
        grade_sections=grade_sections,
        page_title="TOC Attendance",
        page_subtitle="Simple attendance form class coverage.",
        active_tool="TOC Attendance",
    )

@toc_bp.route("/search-teachers")
@login_required
@tool_required(TOOL_SLUG)
def search_teachers():
    from flask import jsonify, request
    q = request.args.get("q", "")
    teachers = search_teacher_by_name(q) if q else []
    return jsonify([{"name": t["full_name"], "id": t["user_id"]} for t in teachers])

@toc_bp.route("/select_course/<teacher_id>", methods=["GET","POST"])
@login_required
@tool_required(TOOL_SLUG)
def select_course(teacher_id):
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
    teachers = [t["full_name"] for t in get_teachers_in_course(course_id)]

    if request.method == "POST":
        absent_ids = request.form.getlist("absent")
        absent_students = [s for s in students if str(s["user_id"]) in absent_ids]
        submitter = current_user().get("display_name") or current_user().get("username")
        log_attendance(absent_students, course_name, teachers, submitted_by=submitter)
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

@toc_bp.route("/grade/<int:grade_section_id>", methods=["GET", "POST"])
@login_required
@tool_required(TOOL_SLUG)
def take_attendance_grade(grade_section_id):
    students = get_students_in_grade_section(grade_section_id)
    section = get_grade_section(grade_section_id)
    course_name = section["display_name"] if section else "Unknown Grade"

    if request.method == "POST":
        absent_ids = request.form.getlist("absent")
        absent_students = [s for s in students if str(s["user_id"]) in absent_ids]
        submitter = current_user().get("display_name") or current_user().get("username")
        log_attendance(absent_students, course_name, submitted_by=submitter)
        log_attendance(absent_students, course_name, [], submitted_by=submitter)
        return render_template(
            "take_attendance.html",
            students=students,
            submitted=True,
            absent_ids=absent_ids,
            course_name=course_name,
            teacher_id=None,
            page_title="TOC Attendance",
            page_subtitle="Simple attendance form for senior school coverage.",
            active_tool="TOC Attendance",
        )
    return render_template(
        "take_attendance.html",
        students=students,
        submitted=False,
        course_name=course_name,
        teacher_id=None,
        page_title="TOC Attendance",
        page_subtitle="Simple attendance form for senior school coverage.",
        active_tool="TOC Attendance",
    )