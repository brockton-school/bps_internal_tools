"""Import Canvas SIS export CSVs into the application's MariaDB database.

This script replaces the old SQLite importer and now operates directly on the
MariaDB schema used by the application.  It reads `courses.csv`,
`users.csv`, and `enrollments.csv` from a directory and applies the changes to
the database:

* Rows with matching primary keys are **updated** – only the columns present in
  the CSV are touched, so existing data in other columns remains intact.
* Rows that exist in the database but not in the CSV are **removed**.
* For `enrollments`, the table is replaced entirely with the contents of the
  CSV (i.e. it mirrors the CSV exactly).

Usage (from repository root)::

    python -m scripts.import_to_sqlite --db <DB_URL> --dir env/sis_export

The database URL defaults to the ``DATABASE_URL`` environment variable and the
CSV directory defaults to ``env/sis_export``.
"""

import argparse
import os
from typing import Optional, Type

import pandas as pd
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from bps_internal_tools.models import Base, Course, People, Enrollment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import Canvas SIS CSV exports into MariaDB",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("DATABASE_URL"),
        help="SQLAlchemy database URL (defaults to DATABASE_URL env var)",
    )
    parser.add_argument(
        "--dir",
        default=os.getenv("SIS_EXPORT_DIR", "env/sis_export"),
        help="Directory containing courses.csv, users.csv, enrollments.csv",
    )
    return parser.parse_args()


def load_csv(path: str) -> Optional[pd.DataFrame]:
    """Load a CSV file into a DataFrame if it exists."""
    if not os.path.exists(path):
        print(f"⚠️  CSV not found: {path}")
        return None
    return pd.read_csv(path)


def upsert_from_df(session: Session, model: Type[Base], df: pd.DataFrame, pk: str) -> None:
    """Upsert rows from *df* into *model* and remove missing rows."""
    if df is None:
        return

    csv_ids = set()
    for _, row in df.iterrows():
        data = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        pk_val = data[pk]
        csv_ids.add(pk_val)
        obj = session.get(model, pk_val)
        if obj:
            for col, val in data.items():
                setattr(obj, col, val)
        else:
            session.add(model(**data))

    session.flush()
    # Remove rows not present in the CSV
    if csv_ids:
        session.query(model).filter(~getattr(model, pk).in_(csv_ids)).delete(
            synchronize_session=False
        )
    session.commit()


def replace_enrollments(session: Session, df: pd.DataFrame) -> None:
    """Replace the enrollments table contents with *df* (mirror CSV)."""
    if df is None:
        return

    session.execute(delete(Enrollment))
    rows = df.where(pd.notnull(df), None).to_dict(orient="records")
    if rows:
        session.bulk_insert_mappings(Enrollment, rows)
    session.commit()


def main() -> None:
    args = parse_args()
    if not args.db:
        raise SystemExit("❌ Provide a database URL via --db or DATABASE_URL env var")

    engine = create_engine(args.db, future=True)
    # Ensure tables exist (no-op if already present)
    Base.metadata.create_all(engine)

    csv_dir = args.dir
    courses_df = load_csv(os.path.join(csv_dir, "courses.csv"))
    users_df = load_csv(os.path.join(csv_dir, "users.csv"))
    enrollments_df = load_csv(os.path.join(csv_dir, "enrollments.csv"))

    with Session(engine) as session:
        upsert_from_df(session, Course, courses_df, "course_id")
        upsert_from_df(session, People, users_df, "user_id")
        replace_enrollments(session, enrollments_df)

    print("✅ Canvas SIS data imported")


if __name__ == "__main__":
    main()

