"""
Google Sheets writer (optional).
Supports credentials via file path (local) or GOOGLE_CREDS_JSON env var.

Columns written (in order):
    Date | Telegram ID | Username | Region | District | Full name |
    Phone | Parent phone | Status | Source | Comment

If Google credentials or SPREADSHEET_ID are not configured, save_to_sheets()
is a no-op that just logs the record. This lets the bot run without Sheets.
"""

import logging
from config import SHEETS_ENABLED, SPREADSHEET_ID, get_credentials_file

logger = logging.getLogger(__name__)

SCOPES     = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "Registrations"

COLUMN_ORDER = [
    "date",
    "telegram_id",
    "username",
    "region",
    "district",
    "fullname",
    "phone",
    "parent_phone",
    "status",
    "source",
    "comment",
]


def _get_service():
    # Imported lazily so the bot can start without google libs being used
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    creds_file = get_credentials_file()
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def save_to_sheets(record: dict) -> None:
    """Append one row to the Google Sheet (or log it if Sheets is disabled)."""
    if not SHEETS_ENABLED:
        logger.info("[Sheets disabled] Registration: %s", record)
        return

    service = _get_service()
    row     = [record.get(col, "") for col in COLUMN_ORDER]
    range_  = f"{SHEET_NAME}!A:K"

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    logger.info("Saved row for Telegram ID %s", record.get("telegram_id"))
