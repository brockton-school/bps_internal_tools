from .extensions import db
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# --- Auth / RBAC ---
class Role(db.Model):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)     # e.g. 'admin', 'attendance'
    active = Column(Boolean, default=True, nullable=False)

    tools = relationship("RoleTool", back_populates="role", cascade="all, delete-orphan")

class RoleTool(db.Model):
    __tablename__ = "role_tools"
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    tool_slug = Column(String(128), nullable=False)            # e.g. 'toc_attendance'
    __table_args__ = (UniqueConstraint("role_id", "tool_slug", name="uq_role_tool"),)

    role = relationship("Role", back_populates="tools")

class User(db.Model):
    __tablename__ = "users_auth"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)   # was String(255)
    display_name = Column(String(255), nullable=False)
    role_name = Column(String(64), ForeignKey("roles.name"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    auth_provider = Column(String(32), nullable=True)  # identifies log in source
    canvas_user_id = Column(String(64), ForeignKey("users_canvas.user_id"), nullable=True)  # adds support for linking Google Users to Canvas

    
# --- Canvas-like data ---
class Course(db.Model):
    __tablename__ = "courses"
    course_id = Column(String(32), primary_key=True)      # 'c003936' etc.
    integration_id = Column(String(64))
    short_name = Column(String(255))
    long_name = Column(Text)
    account_id = Column(String(64))
    term_id = Column(String(64))
    status = Column(String(32))
    start_date = Column(String(32))
    end_date = Column(String(32))
    course_format = Column(String(64))
    blueprint_course_id = Column(String(64))

class People(db.Model):
    __tablename__ = "users_canvas"
    user_id = Column(String(64), primary_key=True)        # Canvas user_id
    integration_id = Column(String(64))
    authentication_provider_id = Column(String(64))
    login_id = Column(String(255))
    password = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    full_name = Column(String(255))
    sortable_name = Column(String(255))
    short_name = Column(String(255))
    email = Column(String(255))
    status = Column(String(64))
    pronouns = Column(String(255))
    grade = Column(String(64))

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String(32), ForeignKey("courses.course_id", ondelete="CASCADE"), index=True)
    user_id = Column(String(64), ForeignKey("users_canvas.user_id", ondelete="CASCADE"), index=True)
    role = Column(String(64), index=True)                 # 'teacher', 'student'
    role_id = Column(Integer)
    section_id = Column(String(64))
    status = Column(String(64))
    associated_user_id = Column(String(64))
    limit_section_privileges = Column(String(16))
    temporary_enrollment_source_user_id = Column(String(64))

class GradeSection(db.Model):
    __tablename__ = "grade_sections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(255), unique=True, nullable=False)
    school_level = Column(String(64))
    reference_course_id = Column(String(32), ForeignKey("courses.course_id", ondelete="SET NULL"))