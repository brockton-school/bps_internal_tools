import subprocess
import os
import csv

from datetime import datetime, time
import pytz

def format_time(datetime_obj):
    """Formats a datetime object into a 12-hour time string."""
    return datetime_obj.strftime('%I:%M %p')

def get_version_info():
    try:
        # Define the path to the version info file
        commit_hash_file_path = "/app/git_commit.txt"
        version_name_file_path = "/app/git_version.txt"
        
        # Open and read the file
        with open(commit_hash_file_path, "r") as file:
            commit = file.read().strip()

        with open(version_name_file_path, "r") as file:
            version = file.read().strip()
        
        return {
            "version": version,
            "commit": commit
        }
    except FileNotFoundError:
        # Return a default message if the file is not found
        return "Version information not available"
