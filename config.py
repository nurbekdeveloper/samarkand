"""
Load all secrets from environment variables.
Copy .env.example → .env, fill in values, then run:  python bot.py
"""

import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN      = os.environ["BOT_TOKEN"]           # From @BotFather
ADMIN_GROUP_ID = int(os.environ["ADMIN_GROUP_ID"]) # Negative int, e.g. -1001234567890
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]      # Google Sheets ID from URL


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
