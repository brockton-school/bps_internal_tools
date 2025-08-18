# scripts/migrate_to_mariadb.py
import os, csv, argparse, sys
from sqlalchemy import create_engine, text, inspect, select, delete
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

# Import from your project package/root. Run with: python -m scripts.migrate_to_mariadb
from bps_internal_tools.models import Base, Course, People, Enrollment, Role, RoleTool, User

def parse_args():
    p = argparse.ArgumentParser(description="Migrate SQLite + CSV auth to MariaDB (idempotent).")
    p.add_argument("--sqlite", default="sqlite:////home/alan/bps_internal_tools/data/canvas.db",
                   help="SQLAlchemy URL to source SQLite (e.g., sqlite:////home/alan/bps_internal_tools/data/canvas.db)")
    p.add_argument("--maria", default="mysql+pymysql://bps:GDpkjG9TNcn7lv4Ww58w@seymour.nv.alanross.io:3306/bps?charset=utf8mb4",
                   help="SQLAlchemy URL to MariaDB (e.g., mysql+pymysql://user:pass@host/db?charset=utf8mb4)")
    p.add_argument("--users_csv", default=os.getenv("AUTH_USERS_CSV", "env/auth_users.csv"))
    p.add_argument("--roles_csv", default=os.getenv("AUTH_ROLES_CSV", "env/auth_roles.csv"))
    p.add_argument("--strict", action="store_true", help="Fail on first orphan enrollment (default skips).")
    p.add_argument("--dry_run", action="store_true", help="Do not write to destination DB.")
    return p.parse_args()

def require_tables(engine, required):
    insp = inspect(engine)
    have = set(insp.get_table_names())
    missing = [t for t in required if t not in have]
    if missing:
        raise SystemExit(f"❌ Source DB missing tables: {missing}. URL is wrong or DB not initialized.")
    print(f"✅ Found source tables: {sorted(have)}")

def ensure_schema(dst_engine):
    print("Ensuring destination schema exists...")
    Base.metadata.create_all(bind=dst_engine)

def upsert_courses_and_users(src_conn, dst_session, dry_run=False):
    # Courses
    courses = src_conn.execute(text("SELECT * FROM courses")).mappings().all()
    # People (Canvas users)
    users = src_conn.execute(text("SELECT * FROM users")).mappings().all()

    print(f"Upserting courses={len(courses)}, users={len(users)}")
    if dry_run:
        return

    for r in courses:
        dst_session.merge(Course(**dict(r)))  # merge = upsert
    for r in users:
        dst_session.merge(People(**dict(r)))
    dst_session.commit()

def upsert_enrollments(src_conn, dst_session, strict=False, dry_run=False):
    enrollments = src_conn.execute(text("SELECT * FROM enrollments")).mappings().all()
    print(f"Processing enrollments={len(enrollments)}")

    if dry_run:
        print("DRY RUN: skipping enrollments write")
        return

    # Build existence sets from destination
    existing_users = {u[0] for u in dst_session.execute(text("SELECT user_id FROM users_canvas")).all()}
    existing_courses = {c[0] for c in dst_session.execute(text("SELECT course_id FROM courses")).all()}

    good, skipped = 0, 0
    for r in enrollments:
        if (r["user_id"] in existing_users) and (r["course_id"] in existing_courses):
            # merge respects composite PK -> idempotent
            dst_session.merge(Enrollment(**dict(r)))
            good += 1
        else:
            if strict:
                raise SystemExit(f"❌ Orphan enrollment: {r}")
            skipped += 1
    dst_session.commit()
    print(f"Enrollments inserted/updated: {good}, skipped (missing parent): {skipped}")

def looks_like_werkzeug_hash(s: str) -> bool:
    if not s:
        return False
    # Common werkzeug schemes
    return s.startswith("pbkdf2:") or s.startswith("scrypt:")

def upsert_roles_and_users_auth(dst_session, roles_csv, users_csv, dry_run=False):
    # ROLES
    if os.path.exists(roles_csv):
        with open(roles_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("role") or "").strip()
                if not name:
                    continue
                active = (row.get("active","true").strip().lower() != "false")
                tools_raw = (row.get("tools") or "").strip()
                tools = ["*"] if tools_raw == "*" else [t.strip() for t in tools_raw.split(",") if t.strip()]
                print(f"Role upsert: {name} tools={tools} active={active}")

                if dry_run:
                    continue

                # Upsert role
                r = dst_session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
                if not r:
                    r = Role(name=name, active=active)
                    dst_session.add(r); dst_session.flush()
                else:
                    r.active = active
                    dst_session.flush()

                # Upsert tools: replace set (idempotent)
                dst_session.execute(delete(RoleTool).where(RoleTool.role_id == r.id))
                if tools == ["*"]:
                    dst_session.add(RoleTool(role_id=r.id, tool_slug="*"))
                else:
                    for slug in tools:
                        dst_session.add(RoleTool(role_id=r.id, tool_slug=slug))
        if not dry_run:
            dst_session.commit()

    # USERS AUTH
    if os.path.exists(users_csv):
        with open(users_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = (row.get("username") or "").strip().lower()
                if not username:
                    continue
                display_name = (row.get("display_name") or username).strip()
                role_name = (row.get("role") or "user").strip()
                active = (row.get("active","true").strip().lower() != "false")
                pwd_hash = (row.get("password_hash") or "").strip()
                if pwd_hash:
                    if looks_like_werkzeug_hash(pwd_hash):
                        final_hash = pwd_hash                       # keep existing hash
                    else:
                        # Treat as plaintext -> hash with a stable method
                        from werkzeug.security import generate_password_hash
                        final_hash = generate_password_hash(pwd_hash, method="pbkdf2:sha256")
                else:
                    # No password provided -> set temporary one
                    from werkzeug.security import generate_password_hash
                    final_hash = generate_password_hash("changeme123!", method="pbkdf2:sha256")
                print(f"User upsert: {username} role={role_name} active={active}")

                if dry_run:
                    continue

                u = dst_session.execute(select(User).where(User.username == username)).scalar_one_or_none()
                if not u:
                    dst_session.add(User(
                        username=username,
                        display_name=display_name,
                        role_name=role_name,
                        active=active,
                        password_hash=final_hash or generate_password_hash("changeme123!")  # fallback
                    ))
                else:
                    u.display_name = display_name
                    u.role_name = role_name
                    u.active = active
                    if pwd_hash:
                        u.password_hash = pwd_hash
        if not dry_run:
            dst_session.commit()

def main():
    args = parse_args()
    if not args.maria:
        sys.exit("❌ Provide MariaDB DSN via --maria or DATABASE_URL env var.")

    # Engines
    src_engine = create_engine(args.sqlite, future=True)
    dst_engine = create_engine(args.maria, pool_pre_ping=True, future=True)
    DstSession = sessionmaker(bind=dst_engine, future=True, autoflush=False, autocommit=False)

    # Sanity: required source tables
    require_tables(src_engine, required=["courses", "users", "enrollments"])

    # Ensure destination schema
    ensure_schema(dst_engine)

    with src_engine.connect() as src, DstSession() as dst:
        upsert_courses_and_users(src, dst, dry_run=args.dry_run)

    with src_engine.connect() as src, DstSession() as dst:
        upsert_enrollments(src, dst, strict=args.strict, dry_run=args.dry_run)

    with DstSession() as dst:
        upsert_roles_and_users_auth(dst, args.roles_csv, args.users_csv, dry_run=args.dry_run)

    print("✅ Migration complete (idempotent).")

if __name__ == "__main__":
    main()
