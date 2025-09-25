import gspread
from google.oauth2.service_account import Credentials
import os
from config import COLUMN_HEADERS_ARRAY, COLUMN_DATE, COLUMN_ACTION, COLUMN_NAME, COLUMN_REASON, COLUMN_TIME, COLUMN_USER_TYPE, COLUMN_GRADE, COLUMN_PHONE, COLUMN_RETURN_TIME, COLUMNS_TOTAL, COLUMN_CHECK, COLUMNS_TOTAL_INT

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
spreadsheet = client.open_by_key(os.getenv('GOOGLE_SHEET_ID'))

def get_or_create_sheet(sheet_name):
    """Check if a sheet with the given name exists, otherwise create it."""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="500", cols=COLUMNS_TOTAL)
        worksheet.append_row(COLUMN_HEADERS_ARRAY)  # Add headers

        # Bold the header row and freeze it
        bold_format = {
            "repeatCell": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 1  # The first row
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True}
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold"
            }
        }

        # Freeze the first row
        freeze_row_request = {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": worksheet.id,
                    "gridProperties": {
                        "frozenRowCount": 1  # Freeze the first row
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        }

        # Add sort buttons
        sort_button_request = {
            'setBasicFilter': {
                'filter': {
                    'range': {
                        'sheetId': worksheet.id,
                        'startRowIndex': 0,  # Header row starts at 0
                        'startColumnIndex': 0,  # Start from the first column
                        'endColumnIndex': COLUMNS_TOTAL_INT + 1  # Adjust based on your sheet's columns
                    }
                }
            }
        }

        # Bold the Name and Time columns
        bold_name_time_columns = {
            "repeatCell": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 1,  # From the second row (after headers)
                    "endRowIndex": 100,  # Apply to the rest of the rows
                    "startColumnIndex": COLUMN_NAME,  # Name column
                    "endColumnIndex": COLUMN_NAME + 1  # Apply to Name column
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True}
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold"
            }
        }

        bold_time_column = {
            "repeatCell": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 1,  # From the second row (after headers)
                    "endRowIndex": 100,  # Apply to the rest of the rows
                    "startColumnIndex": COLUMN_TIME,  # Time column
                    "endColumnIndex": COLUMN_TIME + 1  # Apply to Time column
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True}
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold"
            }
        }

        # Conditional formatting for Action column (sign-ins green, sign-outs red)
        conditional_formatting_action = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": worksheet.id,
                            "startColumnIndex": COLUMN_ACTION,  # Action column
                            "endColumnIndex": COLUMN_ACTION + 1
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Signing In"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 0.8, "green": 1, "blue": 0.8}
                        }
                    }
                },
                "index": 0
            }
        }

        conditional_formatting_sign_out = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": worksheet.id,
                            "startColumnIndex": COLUMN_ACTION,  # Action column
                            "endColumnIndex": COLUMN_ACTION + 1
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Signing Out"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8}
                        }
                    }
                },
                "index": 1
            }
        }

        # Conditional formatting for User Type column (staff yellow, students blue)
        conditional_formatting_user_type = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": worksheet.id,
                            "startColumnIndex": COLUMN_USER_TYPE,  # User Type column
                            "endColumnIndex": COLUMN_USER_TYPE + 1
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_CONTAINS",
                            "values": [{"userEnteredValue": "Staff"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1, "green": 1, "blue": 0.8}  # Light yellow
                        }
                    }
                },
                "index": 0
            }
        }

        conditional_formatting_student = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": worksheet.id,
                            "startColumnIndex": COLUMN_USER_TYPE,  # User Type column
                            "endColumnIndex": COLUMN_USER_TYPE + 1
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Student"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 1}  # Light blue
                        }
                    }
                },
                "index": 1
            }
        }

        conditional_formatting_visitor = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": worksheet.id,
                            "startColumnIndex": COLUMN_USER_TYPE,  # User Type column
                            "endColumnIndex": COLUMN_USER_TYPE + 1
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Visitor"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.9}  # Light pink
                        }
                    }
                },
                "index": 2
            }
        }

        checkbox_column_setup = {
            'repeatCell': {
                'range': {
                    'sheetId': worksheet.id,
                    'startColumnIndex': COLUMN_CHECK,  # Adjust the column index as needed
                    'endColumnIndex': COLUMN_CHECK + 1,
                    'startRowIndex': 1,  # Skip header row
                },
                'cell': {
                    'dataValidation': {
                        'condition': {
                            'type': 'BOOLEAN'
                        },
                        'strict': True,
                        'showCustomUi': True
                    }
                },
                'fields': 'dataValidation'
            }
        }

        # Apply the formatting requests and conditional formatting in a single batch update
        spreadsheet.batch_update({
            "requests": [
                bold_format,
                freeze_row_request,
                sort_button_request,
                bold_name_time_columns,
                bold_time_column,
                conditional_formatting_action,
                conditional_formatting_sign_out,
                conditional_formatting_user_type,
                conditional_formatting_visitor,
                conditional_formatting_student,
                checkbox_column_setup
            ]
        })

    return worksheet