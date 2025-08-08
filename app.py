from flask import Flask, render_template, request, redirect, url_for, jsonify
from queries import search_teacher_by_name, get_courses_for_user, get_students_in_course, get_course_info
from config import DEFAULT_TERMS
from sheets import log_attendance
from utils import get_version_info

app = Flask(__name__)

@app.context_processor
def inject_footer_info():
    return {
        "version_info": get_version_info(),
        "copyright_text": "© 2025 Brockton School. All rights reserved."
    }

@app.route('/', methods=['GET', 'POST'])
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
def select_course(teacher_id):
    if request.method == 'POST':
        course_id = request.form['course_id']
        return redirect(url_for('take_attendance', course_id=course_id, teacher_id=teacher_id))
    courses = get_courses_for_user(teacher_id, role='teacher', terms=DEFAULT_TERMS)
    return render_template('select_course.html', courses=courses, teacher_id=teacher_id)

@app.route('/take_attendance/<course_id>', methods=['GET','POST'])
def take_attendance(course_id):
    students = get_students_in_course(course_id)
    info = get_course_info(course_id)  # returns {'short_name':..., 'long_name':...}
    course_name = info.get('long_name') or info.get('short_name') or 'Unknown Course'
    teacher_id = request.args.get('teacher_id')  # passed via redirect above

    if request.method == 'POST':
        absent_ids = request.form.getlist('absent')
        absent_students = [s for s in students if str(s['user_id']) in absent_ids]
        log_attendance(absent_students, course_name)
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

