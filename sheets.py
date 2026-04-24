"""
Google Sheets writer.
Supports credentials via file path (local) or GOOGLE_CREDS_JSON env var (Render.com).

Columns written (in order):
    Date | Telegram ID | Username | Region | District | Full name |
    Phone | Parent phone | Status | Source | Comment
"""

import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import SPREADSHEET_ID, get_credentials_file

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
    creds_file = get_credentials_file()
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def save_to_sheets(record: dict) -> None:
    """Append one row to the Google Sheet."""
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
