from typing import Dict, List, Optional

from sqlalchemy import func, select

from bps_internal_tools.extensions import db
from bps_internal_tools.models import Course, Enrollment, GradeSection, People


_ACTIVE_STATUS = "active"


# Reusable predicate: real Canvas courses c + digits only (e.g., c003936)
_COURSE_ID_REGEX = r'^c[0-9]+$'

def search_teacher_by_name(query):
    q = f"%{query.lower()}%"
    s = db.session
    rows = s.execute(
        select(People.user_id, People.full_name)
        .join(Enrollment, Enrollment.user_id == People.user_id)
        .where(Enrollment.role == "teacher")
        .where(Enrollment.course_id.like("c%"))
        .where(People.full_name.ilike(q))
        .where(People.status == 'active')
    ).all()
    # DISTINCT-like (SQLA 2.0 distinct over tuple is possible; or dedupe in Python)
    seen, out = set(), []
    for uid, name in rows:
        if uid not in seen:
            out.append({"user_id": uid, "full_name": name})
            seen.add(uid)
    return out

def get_courses_for_user(user_id: str, role: str | None = None, terms: list[str] | None = None):
    s = db.session
    order_key = func.coalesce(Course.long_name, Course.short_name, Course.course_id)

    stmt = (
        select(Course.course_id, Course.short_name, Course.long_name)
        .join(Enrollment, Enrollment.course_id == Course.course_id)
        .where(Enrollment.user_id == user_id)
        .where(Course.course_id.op('REGEXP')(r'^c[0-9]+$'))
    )
    if role:
        stmt = stmt.where(Enrollment.role == role)
    if terms:
        stmt = stmt.where(Course.term_id.in_(terms))

    rows = s.execute(stmt.distinct().order_by(order_key, Course.course_id)).all()

    return [
        {"course_id": cid, "short_name": sname, "long_name": lname}
        for (cid, sname, lname) in rows
    ]


def get_students_in_course(course_id: str) -> List[Dict]:
    """
    Return active students (Canvas users) in a given course_id (user_id + full_name).
    """
    s = db.session
    stmt = (
        select(People.user_id, People.full_name)
        .join(Enrollment, Enrollment.user_id == People.user_id)
        .where(Enrollment.course_id == course_id)
        .where(Enrollment.role == 'student')
        .where(People.status == 'active')
        .order_by(People.full_name)
    )
    rows = s.execute(stmt).all()

    return [{"user_id": uid, "full_name": full} for (uid, full) in rows]

def get_teachers_in_course(course_id: str) -> List[Dict]:
    """Return teachers (Canvas users) in a given course."""
    s = db.session
    stmt = (
        select(People.user_id, People.full_name)
        .join(Enrollment, Enrollment.user_id == People.user_id)
        .where(Enrollment.course_id == course_id)
        .where(Enrollment.role == "teacher")
        .order_by(People.full_name)
    )
    rows = s.execute(stmt).all()

    return [{"user_id": uid, "full_name": full} for (uid, full) in rows]


def get_course_info(course_id: str) -> Dict:
    """
    Return {'short_name': ..., 'long_name': ...} for a course_id,
    or sensible fallbacks if not found.
    """
    s = db.session
    row = s.execute(
        select(Course.short_name, Course.long_name)
        .where(Course.course_id == course_id)
    ).first()

    if not row:
        return {"short_name": "", "long_name": "Unknown Course"}
    short, long_ = row
    return {"short_name": short or "", "long_name": long_ or (short or "Unknown Course")}

def get_grade_sections() -> List[Dict]:
    """Return all grade sections."""
    s = db.session
    rows = s.execute(
        select(GradeSection.id, GradeSection.display_name)
        .order_by(GradeSection.display_name)
    ).all()
    return [{"id": gid, "display_name": name} for gid, name in rows]

def get_grade_section(section_id: int) -> Optional[Dict]:
    """Return a grade section by id."""
    s = db.session
    row = s.execute(
        select(
            GradeSection.id,
            GradeSection.display_name,
            GradeSection.school_level,
            GradeSection.reference_course_id,
            GradeSection.reference_is_section,
        ).where(GradeSection.id == section_id)
    ).first()
    if not row:
        return None
    gid, name, level, course_id, is_section = row
    return {
        "id": gid,
        "display_name": name,
        "school_level": level,
        "reference_course_id": course_id,
        "reference_is_section": is_section,
    }

def get_students_in_grade_section(section_id: int) -> List[Dict]:
    """Return active students for a given grade section."""
    info = get_grade_section(section_id)
    if not info or not info["reference_course_id"]:
        return []
    ref_id = info["reference_course_id"]
    s = db.session
    stmt = select(People.user_id, People.full_name).join(
        Enrollment, Enrollment.user_id == People.user_id
    )
    if info.get("reference_is_section"):
        stmt = stmt.where(Enrollment.section_id == ref_id)
    else:
        stmt = stmt.where(Enrollment.course_id == ref_id)
    stmt = (
        stmt.where(Enrollment.role == 'student')
        .where(People.status == 'active')
        .order_by(People.full_name)
    )
    rows = s.execute(stmt).all()
    return [{"user_id": uid, "full_name": full} for (uid, full) in rows]


def get_grades() -> List[str]:
    """Return a sorted list of distinct grades for active Canvas users."""

    grade_rows = (
        db.session.query(func.trim(People.grade))
        .filter(func.lower(People.status) == _ACTIVE_STATUS)
        .filter(People.grade.isnot(None))
        .filter(func.trim(People.grade) != "")
        .distinct()
        .order_by(func.lower(People.grade))
        .all()
    )

    return [row[0] for row in grade_rows]

def get_personnel_suggestions(query: str, user_type: str, grade: str) -> List[str]:
    """Return a list of matching names for the provided query."""

    if not query:
        return []

    query = query.strip()
    if not query:
        return []

    people_query = db.session.query(People.full_name).filter(
        func.lower(People.status) == _ACTIVE_STATUS
    )

    if user_type == "Staff":
        people_query = people_query.filter(
            (People.grade.is_(None)) | (func.trim(People.grade) == "")
        )
    elif user_type == "Student":
        if grade:
            people_query = people_query.filter(
                func.lower(func.trim(People.grade)) == grade.lower()
            )
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
        .filter(func.lower(People.status) == _ACTIVE_STATUS)
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
        .filter(func.lower(People.status) == _ACTIVE_STATUS)
        .filter(func.lower(func.trim(People.grade)) == grade.lower())
        .order_by(People.full_name)
        .all()
    )

    return [row[0] for row in results]

