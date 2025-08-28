import csv
import io
import re
from datetime import datetime
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    current_app,
    flash,
)
from sqlalchemy import select

from bps_internal_tools.extensions import db
from bps_internal_tools.models import People, UserImport, UserChangeLog
from bps_internal_tools.services.auth import login_required, tool_required
from bps_internal_tools.services.canvas import CanvasAPIError, sis_import
from . import sis_sync_bp, TOOL_SLUG


@sis_sync_bp.route("/", methods=["GET"])
@login_required
@tool_required(TOOL_SLUG)
def index():
    return render_template(
        "sis_sync_index.html",
        page_title="SIS Sync",
        page_subtitle="Sync users from MySchool",
        active_tool="SIS Sync",
    )


def _format_user_id(raw_id: str) -> str:
    try:
        num = int(raw_id)
        return f"u{num:06d}"
    except (TypeError, ValueError):
        return ""


@sis_sync_bp.route("/import", methods=["POST"])
@login_required
@tool_required(TOOL_SLUG)
def import_csv():
    file = request.files.get("file")
    if not file:
        flash("No file uploaded", "error")
        return redirect(url_for("sis_sync.index"))

    text = file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    incoming = []
    for row in reader:
        uid = _format_user_id(row.get("USER ID"))
        if not uid:
            continue
        incoming.append({
            "user_id": uid,
            "first_name": row.get("NAME", "").strip(),
            "last_name": row.get("SURNAME", "").strip(),
            "email": (row.get("EMAIL", "") or "").lower(),
            "grade": row.get("CLASS LEVEL", "").strip(),
        })

    existing = {p.user_id: p for p in db.session.scalars(select(People)).all() if re.match(r"^u\d{6}$", p.user_id or "")}

    seen_ids = set()
    now = datetime.utcnow()
    import_log = UserImport(imported_at=now)
    db.session.add(import_log)
    db.session.flush()

    for data in incoming:
        uid = data["user_id"]
        seen_ids.add(uid)
        person = existing.get(uid)
        if person:
            changes = {}
            if data["first_name"] and person.first_name != data["first_name"]:
                changes["first_name"] = (person.first_name, data["first_name"])
                person.first_name = data["first_name"]
            if data["last_name"] and person.last_name != data["last_name"]:
                changes["last_name"] = (person.last_name, data["last_name"])
                person.last_name = data["last_name"]
            full_name = f"{data['first_name']} {data['last_name']}".strip()

            ## Short name is just display name, this is used primarily in spaces where a user may not want a full name shown.
            ## (i.e. on student discaussion board, etc)
            ## currently set to match full name, but in theory this could be first name + last initial... anything goes here.
            short_name = f"{data['first_name']} {data['last_name']}".strip()
            sortable = f"{data['last_name']}, {data['first_name']}".strip(", ")
            if person.full_name != full_name:
                changes["full_name"] = (person.full_name, full_name)
                person.full_name = full_name
            if person.short_name != short_name:
                changes["short_name"] = (person.short_name, short_name)
                person.short_name = short_name
            if person.sortable_name != sortable:
                changes["sortable_name"] = (person.sortable_name, sortable)
                person.sortable_name = sortable
            if data["email"] and person.email != data["email"]:
                changes["email"] = (person.email, data["email"])
                person.email = data["email"]
                person.login_id = data["email"]
            if person.grade != data["grade"]:
                changes["grade"] = (person.grade, data["grade"])
                person.grade = data["grade"]
            if person.status != "active":
                old = person.status
                person.status = "active"
                person.status_changed_at = now
                db.session.add(UserChangeLog(import_id=import_log.id, user_id=uid, field="status", old_value=old, new_value="active", changed_at=now))
            if changes:
                person.updated_at = now
                for field, (old, new) in changes.items():
                    db.session.add(UserChangeLog(import_id=import_log.id, user_id=uid, field=field, old_value=old, new_value=new, changed_at=now))
        else:
            full_name = f"{data['first_name']} {data['last_name']}".strip()
            person = People(
                user_id=uid,
                first_name=data["first_name"],
                last_name=data["last_name"],
                full_name=full_name,
                short_name=data["first_name"],
                sortable_name=f"{data['last_name']}, {data['first_name']}".strip(", "),
                email=data["email"],
                login_id=data["email"],
                authentication_provider_id="114",
                grade=data["grade"],
                status="active",
                updated_at=now,
                status_changed_at=now,
            )
            db.session.add(person)
            db.session.add(UserChangeLog(import_id=import_log.id, user_id=uid, field="create", old_value=None, new_value=None, changed_at=now))

    # suspend missing
    for uid, person in existing.items():
        if uid not in seen_ids and person.status != "suspended":
            old = person.status
            person.status = "suspended"
            person.status_changed_at = now
            db.session.add(UserChangeLog(import_id=import_log.id, user_id=uid, field="status", old_value=old, new_value="suspended", changed_at=now))

    db.session.commit()
    flash("Import complete", "success")
    return redirect(url_for("sis_sync.index"))


@sis_sync_bp.route("/export", methods=["GET"])
@login_required
@tool_required(TOOL_SLUG)
def export_users():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "user_id",
        "login_id",
        "first_name",
        "last_name",
        "short_name",
        "sortable_name",
        "full_name",
        "email",
        "status",
        "authentication_provider_id",
        "grade",
    ])
    for p in db.session.scalars(select(People)).all():
        writer.writerow([
            p.user_id,
            p.login_id,
            p.first_name,
            p.last_name,
            p.short_name,
            p.sortable_name,
            p.full_name,
            p.email,
            p.status,
            p.authentication_provider_id,
            p.grade,
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="users.csv",
    )

@sis_sync_bp.route("/push-canvas", methods=["POST"])
@login_required
@tool_required(TOOL_SLUG)
def push_to_canvas():
    base_url = current_app.config.get("CANVAS_API_URL")
    token = current_app.config.get("CANVAS_API_TOKEN")
    account_id = current_app.config.get("CANVAS_ACCOUNT_ID", "1")
    if not base_url or not token:
        flash("Canvas API not configured", "error")
        return redirect(url_for("sis_sync.index"))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "user_id",
        "login_id",
        "first_name",
        "last_name",
        "short_name",
        "sortable_name",
        "full_name",
        "email",
        "status",
        "authentication_provider_id",
        "grade",
    ])
    for p in db.session.scalars(select(People)).all():
        writer.writerow([
            p.user_id,
            p.login_id,
            p.first_name,
            p.last_name,
            p.short_name,
            p.sortable_name,
            p.full_name,
            p.email,
            p.status,
            p.authentication_provider_id,
            p.grade,
        ])
    output.seek(0)
    try:
        sis_import(
            output.getvalue().encode("utf-8"),
            base_url=base_url,
            token=token,
            account_id=account_id,
        )
    except CanvasAPIError as exc:
        flash(f"Canvas import failed: {exc}", "error")
    except Exception as exc:
        flash(f"Canvas import error: {exc}", "error")
    else:
        flash("Canvas import queued", "success")
    return redirect(url_for("sis_sync.index"))


@sis_sync_bp.route("/custom-users", methods=["GET", "POST"])
@login_required
@tool_required(TOOL_SLUG)
def custom_users():
    if request.method == "POST":
        uid = request.form.get("user_id")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = (request.form.get("email") or "").lower()
        status = request.form.get("status", "active")
        now = datetime.utcnow()
        person = db.session.get(People, uid)
        if person:
            person.first_name = first_name
            person.last_name = last_name
            person.full_name = f"{first_name} {last_name}".strip()
            person.short_name = first_name
            person.sortable_name = f"{last_name}, {first_name}".strip(", ")
            if email:
                person.email = email
                person.login_id = email
            if person.status != status:
                person.status_changed_at = now
            person.status = status
            person.updated_at = now
        else:
            person = People(
                user_id=uid,
                first_name=first_name,
                last_name=last_name,
                full_name=f"{first_name} {last_name}".strip(),
                short_name=first_name,
                sortable_name=f"{last_name}, {first_name}".strip(", "),
                email=email,
                login_id=email,
                authentication_provider_id="114",
                status=status,
                updated_at=now,
                status_changed_at=now,
            )
            db.session.add(person)
        db.session.commit()
        return redirect(url_for("sis_sync.custom_users"))

    customs = [p for p in db.session.scalars(select(People)).all() if not re.match(r"^u\d{6}$", p.user_id or "")]
    return render_template(
        "custom_users.html",
        users=customs,
        page_title="Custom Users",
        page_subtitle="Manage non-SIS users",
        active_tool="SIS Sync",
    )