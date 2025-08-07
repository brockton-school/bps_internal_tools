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
