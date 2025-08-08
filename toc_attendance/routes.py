from flask import render_template, request, redirect, url_for
from auth import login_required, current_user
from . import toc_bp
from queries import search_teacher_by_name, get_courses_for_user, get_students_in_course, get_course_info
from sheets import log_attendance
from config import DEFAULT_TERMS

@toc_bp.route("/", methods=["GET"])
@login_required
def home():
    # optional landing page for toc feature; could redirect to teacher search
    return redirect(url_for("toc.index"))

@toc_bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html",
                           page_title="TOC Attendance",
                           page_subtitle="Simple attendance form for senior school coverage.",
                           active_tool="TOC Attendance")

@toc_bp.route("/search-teachers")
@login_required
def search_teachers():
    from flask import jsonify, request
    q = request.args.get("q", "")
    teachers = search_teacher_by_name(q) if q else []
    return jsonify([{"name": t["full_name"], "id": t["user_id"]} for t in teachers])

@toc_bp.route("/select_course/<teacher_id>", methods=["GET","POST"])
@login_required
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
