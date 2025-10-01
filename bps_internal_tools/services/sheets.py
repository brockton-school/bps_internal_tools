from datetime import datetime
import os

import gspread
from gspread_formatting import format_cell_range, CellFormat, TextFormat
from google.oauth2.service_account import Credentials

from bps_internal_tools.services.settings import get_system_tzinfo

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', "/home/alan/bps_internal_tools/env/splendid-sunset-436122-n9-2a123c008b07.json")
TOC_GOOGLE_SHEET_ID = os.getenv('TOC_GOOGLE_SHEET_ID', "1MqP7hlhQIpsFv8o8Y4tefU2p8eDOlUjH3ooP7_40i_M")

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open_by_key(TOC_GOOGLE_SHEET_ID)

def _now_local():
    return datetime.now(get_system_tzinfo())

def get_or_create_today_tab():
    today_name = _now_local().strftime("%Y-%m-%d")
    try:
        ws = sheet.worksheet(today_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=today_name, rows="500", cols="10")
        # Header
        headers = [
            "Date",
            "Time",
            "Absent Students",
            "Course Name",
            "Course Teachers",
            "Submitted By",
        ]
        ws.insert_row(headers, 1)
        # Freeze header
        ws.freeze(rows=1)
        # Widen C, D, E, F
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
                    "properties": {"pixelSize": 260},
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 5, "endIndex": 6},
                    "properties": {"pixelSize": 200},
                    "fields": "pixelSize"
                }
            }
        ]
        sheet.batch_update({"requests": requests})
        # Bold header
        format_cell_range(ws, "A1:F1", CellFormat(textFormat=TextFormat(bold=True)))
    return ws


def bold_row(worksheet, row_number):
    fmt = CellFormat(textFormat=TextFormat(bold=True))
    format_cell_range(worksheet, f'A{row_number}:F{row_number}', fmt)

def log_attendance(absent_students, course_name, teachers, submitted_by):
    ws = get_or_create_today_tab()
    now = _now_local()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    rows = []
    # Bold course line (we'll keep it for readability)
    ws.append_row([course_name, "", "", "", "", ""], value_input_option="RAW")
    # Make the last row bold:
    last = len(ws.get_all_values())
    format_cell_range(ws, f"A{last}:A{last}", CellFormat(textFormat=TextFormat(bold=True)))

    teachers_str = ", ".join(teachers) if teachers else ""
    if absent_students:
        for s in absent_students:
            rows.append([date_str, time_str, s["full_name"], course_name, teachers_str, submitted_by])
    else:
        rows.append([date_str, time_str, "All Students Present", course_name, teachers_str, submitted_by])

    ws.append_rows(rows, value_input_option="RAW")