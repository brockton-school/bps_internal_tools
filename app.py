from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from queries import search_teacher_by_name, get_courses_for_user, get_students_in_course, get_course_info
from auth import authenticate, login_required, current_user
from config import DEFAULT_TERMS
from sheets import log_attendance
from utils import get_version_info
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "dev-key")

@app.context_processor
def inject_auth_user():
    # already injecting version info; just add user
    return {"auth_user": current_user()}

@app.context_processor
def inject_footer_info():
    vi = get_version_info()
    github_repo = "https://github.com/brockton-school/bps_toc-attendance"
    commit_url = f"{github_repo}/commit/{vi['commit']}" if vi['commit'] != "unknown" else None

    return {
        "version_info": vi['version'],
        "commit_hash": vi['commit'],
        "commit_url": commit_url,
        "copyright_text": "© 2025 Brockton School. All rights reserved."
    }

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        return redirect(url_for('select_course', teacher_id=teacher_id))

    query = request.args.get('query')
    teachers = []
    if query:
        teachers = search_teacher_by_name(query)

    return render_template('index.html', teachers=teachers)

@app.route('/select_course/<teacher_id>', methods=['GET','POST'])
@login_required
def select_course(teacher_id):
    if request.method == 'POST':
        course_id = request.form['course_id']
        return redirect(url_for('take_attendance', course_id=course_id, teacher_id=teacher_id))
    courses = get_courses_for_user(teacher_id, role='teacher', terms=DEFAULT_TERMS)
    return render_template('select_course.html', courses=courses, teacher_id=teacher_id)

@app.route('/take_attendance/<course_id>', methods=['GET','POST'])
@login_required
def take_attendance(course_id):
    students = get_students_in_course(course_id)
    info = get_course_info(course_id)  # returns {'short_name':..., 'long_name':...}
    course_name = info.get('long_name') or info.get('short_name') or 'Unknown Course'
    teacher_id = request.args.get('teacher_id')  # passed via redirect above

    if request.method == 'POST':
        absent_ids = request.form.getlist('absent')
        absent_students = [s for s in students if str(s['user_id']) in absent_ids]
        submitter = current_user().get("display_name") or current_user().get("username")
        log_attendance(absent_students, course_name, submitter)
        return render_template('take_attendance.html',
                               students=students,
                               submitted=True,
                               absent_ids=absent_ids,
                               course_name=course_name,
                               teacher_id=teacher_id)
    return render_template('take_attendance.html',
                           students=students,
                           submitted=False,
                           course_name=course_name,
                           teacher_id=teacher_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = authenticate(username, password)
        if user:
            session["user"] = user
            nxt = request.args.get("next") or url_for("index")
            return redirect(nxt)
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route('/search_teachers', methods=['GET'])
def search_teachers():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    teachers = search_teacher_by_name(query)
    return jsonify([
        {'name': teacher['full_name'], 'id': teacher['user_id']}
        for teacher in teachers
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

