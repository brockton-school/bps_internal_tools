import sqlite3
import pandas as pd

# File paths
COURSES_CSV = '../env/sis_export/courses.csv'
ENROLLMENTS_CSV = '../env/sis_export/enrollments.csv'
USERS_CSV = '../env/sis_export/users.csv'
DB_FILE = '../data/canvas.db'

# Connect to SQLite database (or create it)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Enable foreign key constraint support
cursor.execute('PRAGMA foreign_keys = ON;')

# Drop tables if they already exist (for re-run purposes)
cursor.execute('DROP TABLE IF EXISTS enrollments')
cursor.execute('DROP TABLE IF EXISTS courses')
cursor.execute('DROP TABLE IF EXISTS users')

# Create tables
cursor.execute('''
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    integration_id TEXT,
    authentication_provider_id TEXT,
    login_id TEXT,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    sortable_name TEXT,
    short_name TEXT,
    email TEXT,
    status TEXT,
    pronouns TEXT
)
''')

cursor.execute('''
CREATE TABLE courses (
    course_id TEXT PRIMARY KEY,
    integration_id TEXT,
    short_name TEXT,
    long_name TEXT,
    account_id TEXT,
    term_id TEXT,
    status TEXT,
    start_date TEXT,
    end_date TEXT,
    course_format TEXT,
    blueprint_course_id TEXT
)
''')

cursor.execute('''
CREATE TABLE enrollments (
    course_id TEXT,
    user_id TEXT,
    role TEXT,
    role_id INTEGER,
    section_id TEXT,
    status TEXT,
    associated_user_id TEXT,
    limit_section_privileges TEXT,
    temporary_enrollment_source_user_id TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
)
''')

# Load CSVs into pandas
users_df = pd.read_csv(USERS_CSV)
courses_df = pd.read_csv(COURSES_CSV)
enrollments_df = pd.read_csv(ENROLLMENTS_CSV)

# Write DataFrames to SQLite
users_df.to_sql('users', conn, if_exists='append', index=False)
courses_df.to_sql('courses', conn, if_exists='append', index=False)
enrollments_df.to_sql('enrollments', conn, if_exists='append', index=False)

# Commit and close
conn.commit()
conn.close()

print("✅ Data successfully imported into canvas.db")
