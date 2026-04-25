# Samarkand Academic Lyceum — Telegram Registration Bot

## Overview
A Telegram bot built with **Python 3.12** and **aiogram 3.x** that collects
candidate registrations for the Samarkand Academic Lyceum (IIV).
All bot messages are in Uzbek.

## Architecture
- **bot.py** — main entry point, FSM handlers, registration flow
- **config.py** — env var loader (BOT_TOKEN, ADMIN_GROUP_ID, optional Sheets vars)
- **sheets.py** — optional Google Sheets writer (no-op when not configured)
- Built-in tiny HTTP server on port 8080 for health checks
- Long-polling via aiogram (no webhook required)

## Required Secrets
- `BOT_TOKEN` — Telegram bot token from @BotFather
- `ADMIN_GROUP_ID` — numeric chat id of the admin group (e.g. `-1001234567890`)

## Optional Secrets (Google Sheets integration)
- `SPREADSHEET_ID` — the sheet's long ID (or full URL)
- `GOOGLE_CREDS_JSON` — full contents of a Google service-account JSON key
  (or set `GOOGLE_CREDS_FILE` to a local path)

When Sheets is not configured, registrations are still logged to console
and forwarded to the admin Telegram group.

## Workflow
- **Telegram Bot** — runs `python bot.py`, console output, port 8080 (health check)

## Deployment
Deploy as a **Reserved VM** (long-running process) so that the polling loop
stays alive 24/7.

## Recent Changes
- 2026-04-25: Initial Replit setup. Made Google Sheets fully optional so
  the bot can run with just `BOT_TOKEN` + `ADMIN_GROUP_ID`.
