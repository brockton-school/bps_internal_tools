import gspread
from gspread_formatting import format_cell_range, CellFormat, TextFormat
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')
#SERVICE_ACCOUNT_FILE = "env/splendid-sunset-436122-n9-2a123c008b07.json"
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
#GOOGLE_SHEET_ID = "1MqP7hlhQIpsFv8o8Y4tefU2p8eDOlUjH3ooP7_40i_M"

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open_by_key(GOOGLE_SHEET_ID)

def get_or_create_today_tab():
    today_name = datetime.now().strftime("%Y-%m-%d")
    try:
        worksheet = sheet.worksheet(today_name)
    except gspread.exceptions.WorksheetNotFound:
        # Create new sheet
        worksheet = sheet.add_worksheet(title=today_name, rows="100", cols="10")

        # Add header row
        headers = ["Date", "Time", "Absent Students", "Course Name"]
        worksheet.insert_row(headers, 1)

        # Freeze the header row
        worksheet.freeze(rows=1)

        # Adjust column widths (Google Sheets API batch_update)
        # Note: gspread uses spreadsheets().batchUpdate for formatting
        requests = [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 2,  # 0-based index for "Absent Students" column
                        "endIndex": 3
                    },
                    "properties": {
                        "pixelSize": 250
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,  # "Course Name" column
                        "endIndex": 4
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            }
        ]
        sheet.batch_update({"requests": requests})

    return worksheet


def bold_row(worksheet, row_number):
    fmt = CellFormat(textFormat=TextFormat(bold=True))
    format_cell_range(worksheet, f'A{row_number}:D{row_number}', fmt)

def log_attendance(absent_students, course_name):
    print("TEST THINGS:")
    print(absent_students)
    print(course_name)
    worksheet = get_or_create_today_tab()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    existing_rows = len(worksheet.get_all_values())
    start_row = existing_rows + 1

    # Add bold course name row
    worksheet.update(f"A{start_row}", [[course_name]])
    bold_row(worksheet, start_row)
    start_row += 1

    if absent_students:
        data = [[date_str, time_str, student['full_name'], course_name] for student in absent_students]
        worksheet.update(f"A{start_row}", data)
    else:
        worksheet.update(f"A{start_row}", [[date_str, time_str, "All Students Present", course_name]])