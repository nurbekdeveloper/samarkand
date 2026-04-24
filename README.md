# Samarkand Academic Lyceum — Telegram Registration Bot

A complete Telegram bot for collecting candidate registrations.
Built with **Python 3.11+**, **aiogram 3.x**, and **Google Sheets API v4**.

---

## Files

```
samarkand_bot/
├── bot.py            # Main bot logic + all handlers
├── sheets.py         # Google Sheets writer
├── config.py         # Environment variable loader
├── requirements.txt  # Python dependencies
├── .env.example      # Copy this to .env and fill in secrets
└── credentials.json  # Your Google service account key (you create this)
```

---

## Step 1 — Create the Telegram bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts.
3. Copy the **bot token** (looks like `1234567890:ABCabc...`).
4. Optional but recommended: send `/setprivacy` → choose your bot → **Disable**.
   This lets the bot read messages in groups (needed for admin notifications).

---

## Step 2 — Create the admin group

1. Create a new Telegram group (or use an existing one).
2. Add your bot to the group and make it an **admin** (so it can send messages).
3. Send any message in the group.
4. Visit this URL in your browser (replace `<TOKEN>` with your bot token):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
5. Find the `"chat":{"id": ...}` field — it will be a **negative number** like `-1001234567890`.
   That is your `ADMIN_GROUP_ID`.

---

## Step 3 — Set up Google Sheets

### 3a — Create the spreadsheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. Rename the first tab to exactly: **`Registrations`**
3. In row 1, add these headers (one per column, A through K):

   | A | B | C | D | E | F | G | H | I | J | K |
   |---|---|---|---|---|---|---|---|---|---|---|
   | Date | Telegram ID | Username | Region | District | Full name | Phone | Parent phone | Status | Source | Comment |

4. Copy the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/  →  1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms  ←  /edit
   ```

### 3b — Create a service account

1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project (or select an existing one).
3. Go to **APIs & Services → Enable APIs → search "Google Sheets API" → Enable**.
4. Go to **APIs & Services → Credentials → Create Credentials → Service Account**.
5. Give it any name, click **Create and Continue**, skip optional steps, click **Done**.
6. Click on the service account email you just created.
7. Go to the **Keys** tab → **Add Key → Create new key → JSON → Create**.
8. A `credentials.json` file will download — put it in the `samarkand_bot/` folder.

### 3c — Share the spreadsheet with the service account

1. Open your Google Sheet.
2. Click **Share** (top right).
3. In the "Add people" field, paste the **service account email** (found in `credentials.json` as `"client_email"`).
4. Set permission to **Editor** and click **Send**.

---

## Step 4 — Configure environment variables

```bash
cd samarkand_bot
cp .env.example .env
```

Open `.env` and fill in:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_GROUP_ID=-1001234567890
SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_CREDS_FILE=credentials.json
```

---

## Step 5 — Install dependencies and run

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

You should see:
```
2024-01-15 10:00:00 INFO Bot started
```

---

## Step 6 — Test the bot

1. Open Telegram and find your bot by its username.
2. Send `/start` — you should see the welcome message.
3. Tap **Ro'yxatdan o'tish** and complete the flow.
4. Check your Google Sheet — a new row should appear.
5. Check your admin group — a notification should appear.

---

## Running in production (keep it alive 24/7)

## Render (free) ga deploy qilish

Ushbu loyiha `render.yaml` bilan tayyorlangan. Render’da yangi **Blueprint** service ochsangiz, sozlamalar avtomatik olinadi.

1. GitHub repository'ni Render’ga ulang.
2. **New + → Blueprint** ni tanlang.
3. Env vars kiriting:
   - `BOT_TOKEN`
   - `ADMIN_GROUP_ID`
   - `SPREADSHEET_ID`
   - `GOOGLE_CREDS_JSON`  ← `credentials.json` faylining to‘liq JSON matni
4. Quyidagilarni ham tekshiring:
   - `BOT_TOKEN` → BotFather bergan token (masalan `123...:ABC...`)
   - `ADMIN_GROUP_ID` → faqat raqam, manfiy ko‘rinishda (`-100...`)
   - `SPREADSHEET_ID` → Google Sheet URL ichidagi ID qismi (yoki to‘liq URL ham bo‘ladi)
   - `GOOGLE_CREDS_JSON` → service account JSON faylning to‘liq matni
5. Deploy tugagach, loglarda `Bot started` va `Health check server started` yozuvlarini tekshiring.

> Nega `GOOGLE_CREDS_JSON`?
> Render free muhitida fayl saqlash ishonchli emas, shuning uchun service account JSON ni env orqali berish tavsiya etiladi.

### Option A — systemd (Linux VPS)

Create `/etc/systemd/system/samarkand-bot.service`:

```ini
[Unit]
Description=Samarkand Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/samarkand_bot
ExecStart=/home/ubuntu/samarkand_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable samarkand-bot
sudo systemctl start samarkand-bot
sudo systemctl status samarkand-bot
```

### Option B — screen / tmux (quick & simple)

```bash
screen -S bot
python bot.py
# Press Ctrl+A then D to detach
# Reconnect: screen -r bot
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `BOT_TOKEN` not found | Make sure `.env` file exists and is filled in |
| Bot doesn't reply | Check that polling started without errors |
| Google Sheets not saving | Confirm the service account has Editor access to the sheet |
| Admin group notification fails | Make sure bot is admin in the group and `ADMIN_GROUP_ID` is negative |
| `ADMIN_GROUP_ID` xato formatda | Faqat raqam bo‘lishi kerak (`-100...`), `@groupname` ishlamaydi |
| `credentials.json` not found | Check `GOOGLE_CREDS_FILE` in `.env` points to the correct path |
| `Exited with status 1 while running your code` (Render) | Ko‘pincha env var yetishmaydi. Endi ilova yo‘q env var nomini logda aniq ko‘rsatadi (`Missing required environment variable: ...`). Render Environment bo‘limida `BOT_TOKEN`, `ADMIN_GROUP_ID`, `SPREADSHEET_ID`, `GOOGLE_CREDS_JSON` qiymatlarini qayta tekshiring. |
| `pydantic-core`/`maturin` install fails on Render with `Read-only file system` | Use Python `3.11.11` (not `3.14`) so pip downloads prebuilt wheels. This repo now pins it in both `render.yaml`, `runtime.txt`, and `.python-version`. Then redeploy with **Clear build cache & deploy**. |

---

## Security notes

- Never commit `.env` or `credentials.json` to git.
- Add both to `.gitignore`:
  ```
  .env
  credentials.json
  ```
