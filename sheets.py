import gspread
from gspread_formatting import format_cell_range, CellFormat, TextFormat
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open_by_key(GOOGLE_SHEET_ID)

def get_or_create_today_tab():
    today_name = datetime.now().strftime("%Y-%m-%d")
    try:
        ws = sheet.worksheet(today_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=today_name, rows="500", cols="10")
        # Header
        headers = ["Date", "Time", "Absent Students", "Course Name", "Submitted By"]
        ws.insert_row(headers, 1)
        # Freeze header
        ws.freeze(rows=1)
        # Widen C, D, E
        spreadsheet_id = sheet.id
        requests = [
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3},
                    "properties": {"pixelSize": 260},
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4},
                    "properties": {"pixelSize": 260},
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5},
                    "properties": {"pixelSize": 200},
                    "fields": "pixelSize"
                }
            }
        ]
        sheet.batch_update({"requests": requests})
        # Bold header
        format_cell_range(ws, "A1:E1", CellFormat(textFormat=TextFormat(bold=True)))
    return ws


def bold_row(worksheet, row_number):
    fmt = CellFormat(textFormat=TextFormat(bold=True))
    format_cell_range(worksheet, f'A{row_number}:D{row_number}', fmt)

def log_attendance(absent_students, course_name, submitted_by):
    ws = get_or_create_today_tab()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    rows = []
    # Bold course line (we'll keep it for readability)
    ws.append_row([course_name, "", "", "", ""], value_input_option="RAW")
    # Make the last row bold:
    last = len(ws.get_all_values())
    format_cell_range(ws, f"A{last}:A{last}", CellFormat(textFormat=TextFormat(bold=True)))

    if absent_students:
        for s in absent_students:
            rows.append([date_str, time_str, s["full_name"], course_name, submitted_by])
    else:
        rows.append([date_str, time_str, "All Students Present", course_name, submitted_by])

    ws.append_rows(rows, value_input_option="RAW")