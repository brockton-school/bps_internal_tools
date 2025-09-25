import subprocess
import os
import csv

from datetime import datetime, time
import pytz
from config import PERSONNEL_CSV_PATH

def format_time(datetime_obj):
    """Formats a datetime object into a 12-hour time string."""
    return datetime_obj.strftime('%I:%M %p')

def get_version_info():
    try:
        # Define the path to the version info file
        version_file_path = "/app/version_info.txt"
        
        # Open and read the file
        with open(version_file_path, "r") as file:
            version_info = file.read().strip()
        
        return version_info
    except FileNotFoundError:
        # Return a default message if the file is not found
        return "Version information not available"

# Function to read grades from the CSV file
def read_grades_from_csv(file_path):
    grades = []
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            grades.append(row[0])
    return grades

# Function to get suggestions from the CSV file
def get_personnel_suggestions(query, user_type, grade):
    suggestions = []
    with open(PERSONNEL_CSV_PATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            full_name = f"{row['NAME']} {row['SURNAME']}"
            
            # If the query matches the name
            if query.lower() in full_name.lower():
                # If user is Staff, suggest only those without a Class Level (staff)
                if user_type == "Staff" and not row['CLASS LEVEL']:
                    suggestions.append(full_name)
                # If user is a Student, suggest those with matching Class Level
                elif user_type == "Student" and row['CLASS LEVEL'] == grade:
                    suggestions.append(full_name)

    return suggestions

def get_school_level(full_name):
    """
    Given a full name in the format "NAME SURNAME", return the associated SCHOOL LEVEL.
    If the SCHOOL LEVEL is blank or the name isn't found, return an empty string.
    """
    try:
        with open(PERSONNEL_CSV_PATH, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Construct the full name from "NAME" and "SURNAME" columns
                csv_full_name = f"{row['NAME']} {row['SURNAME']}".strip()

                if csv_full_name.lower() == full_name.lower():  # Case-insensitive comparison
                    return row['SCHOOL LEVEL'].strip() if row['SCHOOL LEVEL'].strip() else ""

    except FileNotFoundError:
        print(f"Error: File not found at {PERSONNEL_CSV_PATH}")
    except Exception as e:
        print(f"Error: {e}")

    return ""  # Return empty string if not found or SCHOOL LEVEL is blank

# Function to load users from the CSV file
def load_users_from_csv(filepath="users.csv"):
    print(filepath)
    users = {}
    try:
        with open(filepath, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    username, hashed_password = row
                    users[username] = hashed_password
    except FileNotFoundError:
        print(f"User credentials file not found: {filepath}")
    return users

USERS = load_users_from_csv()

# Helper for preventing reason when end of day sign out
def should_ask_reason_and_return_time(user_type):
    # Get the current time in Vancouver
    vancouver_tz = pytz.timezone("America/Vancouver")
    vancouver_time = datetime.now(vancouver_tz).time()
    cutoff_time = time(14, 0)  # 2:00 PM Vancouver time
    if user_type == "Staff" and vancouver_time > cutoff_time:
        return "false"  # Don't ask for reason/return time
    return "true"  # Ask for reason/return time