import argparse
import csv
import os

from sqlalchemy import create_engine, text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add grade data to users_canvas table"
    )
    parser.add_argument("csv_file", help="CSV with columns user_id and grade")
    parser.add_argument(
        "--db",
        default=os.getenv("DATABASE_URL", "app.db"),
        help="Database path or SQLAlchemy URL (defaults to app.db or DATABASE_URL)",
    )
    args = parser.parse_args()

    # Accept plain file paths for SQLite or full SQLAlchemy URLs
    db_url = args.db
    if "://" not in db_url:
        db_url = f"sqlite:///{db_url}"

    engine = create_engine(db_url, future=True)

    with engine.begin() as conn, open(args.csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row.get("user_id")
            grade = row.get("grade")
            if not user_id or grade is None:
                continue
            conn.execute(
                text("UPDATE users_canvas SET grade = :grade WHERE user_id = :user_id"),
                {"grade": grade, "user_id": user_id},
            )

    print("✅ Grades imported")


if __name__ == "__main__":
    main()