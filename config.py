"""
Load all secrets from environment variables.
Copy .env.example → .env, fill in values, then run: python bot.py
"""

import os
import re
import tempfile
from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Check Render Environment tab or your local .env file."
        )
    return value


def _normalize_spreadsheet_id(value: str) -> str:
    """
    Accept either:
      - raw spreadsheet ID (recommended), or
      - full Google Sheets URL.
    Returns the spreadsheet ID.
    """
    value = value.strip()
    if "docs.google.com/spreadsheets" not in value:
        return value

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", value)
    if not match:
        raise RuntimeError(
            "SPREADSHEET_ID looks like a URL, but ID could not be parsed. "
            "Provide either the raw ID or a valid Google Sheets URL."
        )
    return match.group(1)


def _parse_admin_group_id(value: str) -> int:
    """
    Parse ADMIN_GROUP_ID as integer and provide a clear error message
    when a non-numeric value is supplied.
    """
    try:
        return int(value.strip())
    except ValueError as exc:
        raise RuntimeError(
            "ADMIN_GROUP_ID must be a numeric Telegram chat id (example: -1001234567890)."
        ) from exc


BOT_TOKEN = _required_env("BOT_TOKEN")  # From @BotFather
ADMIN_GROUP_ID = _parse_admin_group_id(_required_env("ADMIN_GROUP_ID"))  # Negative int, e.g. -1001234567890
SPREADSHEET_ID = _normalize_spreadsheet_id(_required_env("SPREADSHEET_ID"))


def get_credentials_file() -> str:
    """
    Returns path to credentials.json.
    If GOOGLE_CREDS_JSON env var is set (Render.com), writes it to a temp file.
    Otherwise falls back to GOOGLE_CREDS_FILE path (local dev).
    """
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    if creds_json:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write(creds_json)
            tmp.flush()
            return tmp.name
    return os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
