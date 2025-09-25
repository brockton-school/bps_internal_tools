import pandas as pd
import os
import logging
from datetime import datetime
import openpyxl

from config import LOCAL_STORAGE_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_to_local_file(entry):
    """Save the entry to a local Excel file."""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%B")
    day = now.strftime("%Y-%m-%d")

    # Define the directory and file path
    directory_path = os.path.join(LOCAL_STORAGE_PATH, year, month)
    file_path = os.path.join(directory_path, f"{day}.xlsx")

    try:
        os.makedirs(directory_path, exist_ok=True)  # Attempt to create the directory
    except OSError as e:
        logging.error(f"Failed to create directory {directory_path}: {e}")
        return  # Exit the function gracefully

    # Create a DataFrame for the entry
    df = pd.DataFrame([entry])

    try:
        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            updated_df = pd.concat([existing_df, df], ignore_index=True)
            updated_df.to_excel(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)
    except Exception as e:
        logging.error(f"Failed to save file {file_path}: {e}")