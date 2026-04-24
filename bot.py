"""
Samarkand Academic Lyceum - Telegram Registration Bot
Uzbek messages · Python 3.11+ · aiogram 3.x · Google Sheets API
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import BOT_TOKEN, ADMIN_GROUP_ID
from sheets import save_to_sheets

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────
# States
# ──────────────────────────────────────────────────────────
class Registration(StatesGroup):
    region   = State()
    district = State()
    fullname = State()
    phone    = State()
    parent   = State()


# ──────────────────────────────────────────────────────────
# Static data
# ──────────────────────────────────────────────────────────
REGIONS = [
    "Qoraqalpog'iston Respublikasi",
    "Andijon viloyati",
    "Buxoro viloyati",
    "Farg'ona viloyati",
    "Jizzax viloyati",
    "Xorazm viloyati",
    "Namangan viloyati",
    "Navoiy viloyati",
    "Qashqadaryo viloyati",
    "Samarqand viloyati",
    "Sirdaryo viloyati",
    "Surxondaryo viloyati",
    "Toshkent viloyati",
    "Toshkent shahri",
]

SAMARKAND_DISTRICTS = [
    "Samarqand shahri",
    "Kattaqo'rg'on shahri",
    "Bulung'ur tumani",
    "Jomboy tumani",
    "Ishtixon tumani",
    "Kattaqo'rg'on tumani",
    "Narpay tumani",
    "Nurobod tumani",
    "Oqdaryo tumani",
    "Payariq tumani",
    "Pastdarg'om tumani",
    "Paxtachi tumani",
    "Samarqand tumani",
    "Toyloq tumani",
    "Urgut tumani",
    "Qo'shrabot tumani",
]


# ──────────────────────────────────────────────────────────
# Keyboard builders
# ──────────────────────────────────────────────────────────
def region_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(REGIONS), 2):
        row = [InlineKeyboardButton(text=REGIONS[i], callback_data=f"region:{REGIONS[i]}")]
        if i + 1 < len(REGIONS):
            row.append(InlineKeyboardButton(text=REGIONS[i+1], callback_data=f"region:{REGIONS[i+1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def district_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(SAMARKAND_DISTRICTS), 2):
        row = [InlineKeyboardButton(text=SAMARKAND_DISTRICTS[i], callback_data=f"district:{SAMARKAND_DISTRICTS[i]}")]
        if i + 1 < len(SAMARKAND_DISTRICTS):
            row.append(InlineKeyboardButton(text=SAMARKAND_DISTRICTS[i+1], callback_data=f"district:{SAMARKAND_DISTRICTS[i+1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📋 Ro'yxatdan o'tish", callback_data="start_registration")]]
    )


# ──────────────────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────────────────
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Show welcome message and registration button."""
    await state.clear()
    text = (
        "🚨 <b>DIQQAT! SAMARQAND IIV AKADEMIK LITSEY NOMZODLARI UCHUN MAXSUS BOT</b> 🚨\n\n"
        "Siz O'zbekiston Respublikasi Ichki ishlar vazirligi tizimidagi "
        "Samarqand akademik litseyiga hujjat topshirdingizmi?\n\n"
        "Endi siz uchun eng muhim bosqich — psixologik test va saralash jarayoni boshlanmoqda!\n\n"
        "Ushbu bot orqali siz:\n"
        "✅ Psixologik testlar haqida aniq ma'lumot olasiz\n"
        "✅ Eng so'nggi yangiliklar va o'zgarishlardan xabardor bo'lasiz\n"
        "✅ Tayyorgarlik uchun foydali materiallar olasiz\n"
        "✅ Shaxsiy maslahat va yo'naltirish uchun ro'yxatdan o'tasiz\n\n"
        "Ro'yxatdan o'tish uchun pastdagi tugmani bosing."
    )
    await message.answer(text, reply_markup=start_keyboard(), parse_mode="HTML")


@dp.callback_query(F.data == "start_registration")
async def ask_region(callback: CallbackQuery, state: FSMContext):
    """Step 1 – choose region."""
    await state.set_state(Registration.region)
    await callback.message.answer("🌍 Viloyatingizni tanlang:", reply_markup=region_keyboard())
    await callback.answer()


@dp.callback_query(F.data.startswith("region:"))
async def process_region(callback: CallbackQuery, state: FSMContext):
    """Store region; if Samarkand → ask district, else → ask fullname."""
    region = callback.data.split(":", 1)[1]
    await state.update_data(region=region)

    if region == "Samarqand viloyati":
        await state.set_state(Registration.district)
        await callback.message.answer("🏙 Tuman yoki shahringizni tanlang:", reply_markup=district_keyboard())
    else:
        await state.set_state(Registration.fullname)
        await callback.message.answer(
            "👤 Ism va familiyangizni to'liq yozing.\n"
            "<i>Masalan: Aliyev Akmal</i>",
            parse_mode="HTML",
        )
    await callback.answer()


@dp.callback_query(F.data.startswith("district:"))
async def process_district(callback: CallbackQuery, state: FSMContext):
    """Store district → ask fullname."""
    district = callback.data.split(":", 1)[1]
    await state.update_data(district=district)
    await state.set_state(Registration.fullname)
    await callback.message.answer(
        "👤 Ism va familiyangizni to'liq yozing.\n"
        "<i>Masalan: Aliyev Akmal</i>",
        parse_mode="HTML",
    )
    await callback.answer()


@dp.message(Registration.fullname)
async def process_fullname(message: Message, state: FSMContext):
    """Store fullname → ask phone via contact button."""
    await state.update_data(fullname=message.text.strip())
    await state.set_state(Registration.phone)
    await message.answer(
        "📞 Telefon raqamingizni yuboring.\n"
        "Pastdagi tugmani bosing:",
        reply_markup=contact_keyboard(),
    )


@dp.message(Registration.phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    """Store phone from contact share → ask parent phone."""
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await state.update_data(phone=phone)
    await state.set_state(Registration.parent)
    await message.answer(
        "👨‍👩‍👧 Ota yoki onangizning telefon raqamini yozing.\n"
        "<i>Masalan: +998901234567</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Registration.phone)
async def phone_not_shared(message: Message):
    """User typed instead of sharing contact."""
    await message.answer(
        "⚠️ Iltimos, pastdagi <b>«📞 Telefon raqamni yuborish»</b> tugmasini bosib "
        "raqamingizni yuboring.",
        parse_mode="HTML",
        reply_markup=contact_keyboard(),
    )


@dp.message(Registration.parent)
async def process_parent_phone(message: Message, state: FSMContext, bot: Bot):
    """Validate parent phone → save to Sheets → notify admin → confirm to user."""
    raw = message.text.strip()

    # Validation
    if not raw.startswith("+998") or len(raw) < 12:
        await message.answer(
            "❌ Telefon raqam noto'g'ri kiritildi. Iltimos, raqamni <b>+998</b> bilan "
            "boshlanadigan formatda qayta yozing.\n"
            "<i>Masalan: +998901234567</i>",
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    user = message.from_user

    record = {
        "date":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "telegram_id":  str(user.id),
        "username":     f"@{user.username}" if user.username else "—",
        "region":       data.get("region", ""),
        "district":     data.get("district", ""),
        "fullname":     data.get("fullname", ""),
        "phone":        data.get("phone", ""),
        "parent_phone": raw,
        "status":       "New",
        "source":       "Telegram bot",
        "comment":      "",
    }

    # Save to Google Sheets
    try:
        save_to_sheets(record)
    except Exception as e:
        logger.error("Google Sheets error: %s", e)
        await message.answer(
            "⚠️ Texnik xatolik yuz berdi. Iltimos, biroz kutib qayta urinib ko'ring."
        )
        return

    # Confirm to user
    await message.answer(
        "✅ <b>Siz muvaffaqiyatli ro'yxatdan o'tdingiz.</b>\n\n"
        "Tez orada mas'ul xodimlarimiz siz bilan bog'lanadi.\n\n"
        "E'tiboringiz uchun rahmat!",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Notify admin group
    admin_text = (
        "🆕 <b>Yangi ro'yxatdan o'tish</b>\n\n"
        f"👤 Ism familiya: <b>{record['fullname']}</b>\n"
        f"📍 Viloyat: {record['region']}\n"
        f"🏙 Tuman/shahar: {record['district'] or '—'}\n"
        f"📞 Telefon raqam: <code>{record['phone']}</code>\n"
        f"👨‍👩‍👧 Ota/ona telefoni: <code>{record['parent_phone']}</code>\n"
        f"🆔 Telegram ID: <code>{record['telegram_id']}</code>\n"
        f"🔗 Username: {record['username']}\n"
        f"🕒 Sana: {record['date']}"
    )
    try:
        await bot.send_message(ADMIN_GROUP_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        logger.error("Admin group notification error: %s", e)

    await state.clear()


# ──────────────────────────────────────────────────────────
# Health check web server (Render.com free tier uchun)
# ──────────────────────────────────────────────────────────
async def health(request):
    return web.Response(text="OK")


async def run_web():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health check server started on port %s", port)


# ──────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────
async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("Bot started")
    await asyncio.gather(
        run_web(),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())
