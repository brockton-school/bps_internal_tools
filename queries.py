import sqlite3
from sqlalchemy import select, func
from db import SessionLocal
from models import Course, People, Enrollment
from typing import List, Dict, Optional


# Reusable predicate: real Canvas courses c + digits only (e.g., c003936)
_COURSE_ID_REGEX = r'^c[0-9]+$'

def search_teacher_by_name(query):
    q = f"%{query.lower()}%"
    with SessionLocal() as s:
        rows = s.execute(
            select(People.user_id, People.full_name)
            .join(Enrollment, Enrollment.user_id == People.user_id)
            .where(Enrollment.role == "teacher")
            .where(Enrollment.course_id.like("c%"))
            .where(People.full_name.ilike(q))
        ).all()
        # DISTINCT-like (SQLA 2.0 distinct over tuple is possible; or dedupe in Python)
        seen, out = set(), []
        for uid, name in rows:
            if uid not in seen:
                out.append({"user_id": uid, "full_name": name})
                seen.add(uid)
        return out

def get_courses_for_user(user_id: str, role: str | None = None, terms: list[str] | None = None):
    with SessionLocal() as s:
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
    Return students (Canvas users) in a given course_id (user_id + full_name).
    """
    with SessionLocal() as s:
        stmt = (
            select(People.user_id, People.full_name)
            .join(Enrollment, Enrollment.user_id == People.user_id)
            .where(Enrollment.course_id == course_id)
            .where(Enrollment.role == 'student')
            .order_by(People.full_name)
        )
        rows = s.execute(stmt).all()

    return [{"user_id": uid, "full_name": full} for (uid, full) in rows]

def get_course_info(course_id: str) -> Dict:
    """
    Return {'short_name': ..., 'long_name': ...} for a course_id,
    or sensible fallbacks if not found.
    """
    with SessionLocal() as s:
        row = s.execute(
            select(Course.short_name, Course.long_name)
            .where(Course.course_id == course_id)
        ).first()

    if not row:
        return {"short_name": "", "long_name": "Unknown Course"}
    short, long_ = row
    return {"short_name": short or "", "long_name": long_ or (short or "Unknown Course")}
