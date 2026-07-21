"""
Umumiy funksiyalar — webapp.py va send_daily.py ikkalasi ham shu fayldan foydalanadi.
"""

import json
import os
from datetime import datetime

import gspread
import pytz
import requests
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# SOZLAMALAR
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])
GROUP_CHAT_ID = int(os.environ["GROUP_CHAT_ID"])
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SHEET_NAME = os.environ.get("SHEET_NAME", "Cash Flow")
STATE_SHEET_NAME = os.environ.get("STATE_SHEET_NAME", "BotState")
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Tashkent")

# service_account.json faylini disk o'rniga muhit o'zgaruvchisidan ham o'qish mumkin
# (Render'da faylni yuklash noqulay bo'lgani uchun, uni bitta uzun matn sifatida saqlaymiz)
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "service_account.json")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

ROWS = {
    "Naqd": 4,
    "Hisob raqam": 5,
    "Plastik karta": 6,
    "Yo'ldagi pul": 9,
}
FIRST_MONTH_COLUMN = 4  # Yanvar = D ustun


# ---------------------------------------------------------------------------
# GOOGLE SHEETS
# ---------------------------------------------------------------------------
def _get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if SERVICE_ACCOUNT_JSON:
        info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(info, scopes=scopes)
    else:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    return gspread.authorize(creds)


def _get_spreadsheet():
    gc = _get_gspread_client()
    return gc.open_by_key(SPREADSHEET_ID)


def get_sheet_values() -> dict[str, float]:
    sh = _get_spreadsheet()
    ws = sh.worksheet(SHEET_NAME)

    month = datetime.now(pytz.timezone(TIMEZONE)).month
    col = FIRST_MONTH_COLUMN + (month - 1)

    values = {}
    for name, row in ROWS.items():
        cell = ws.cell(row, col, value_render_option="UNFORMATTED_VALUE")
        raw = cell.value
        values[name] = float(raw) if raw not in (None, "") else 0.0
    return values


def _get_state_worksheet(sh):
    try:
        return sh.worksheet(STATE_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=STATE_SHEET_NAME, rows=10, cols=2)
        ws.update("A1", [["{}"]])
        return ws


def load_state() -> dict[str, float]:
    sh = _get_spreadsheet()
    ws = _get_state_worksheet(sh)
    raw = ws.acell("A1").value
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def save_state(values: dict[str, float]) -> None:
    sh = _get_spreadsheet()
    ws = _get_state_worksheet(sh)
    ws.update("A1", [[json.dumps(values, ensure_ascii=False)]])


# ---------------------------------------------------------------------------
# XABAR MATNI
# ---------------------------------------------------------------------------
def format_number(n: float) -> str:
    s = f"{n:,.2f}"
    s = s.replace(",", " ").replace(".", ",")
    return s


def build_message(values: dict[str, float], previous: dict[str, float]) -> str:
    lines = []
    for name, val in values.items():
        prev = previous.get(name)
        if prev is None:
            arrow = ""
        elif val > prev:
            arrow = "🔼"
        elif val < prev:
            arrow = "🔽"
        else:
            arrow = "➡️"
        lines.append(f"{name}: {format_number(val)}{arrow}✅")
    today = datetime.now(pytz.timezone(TIMEZONE)).strftime("%d.%m.%Y")
    return f"📊 Kassa hisoboti — {today}\n\n" + "\n".join(lines)


def confirm_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Yuborish", "callback_data": "confirm"},
                {"text": "✏️ Tahrirlash", "callback_data": "edit"},
                {"text": "❌ Bekor qilish", "callback_data": "cancel"},
            ]
        ]
    }


# ---------------------------------------------------------------------------
# TELEGRAM API (oddiy HTTP so'rovlar, kutubxonasiz)
# ---------------------------------------------------------------------------
def tg_send_message(chat_id: int, text: str, reply_markup: dict | None = None) -> dict:
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    r = requests.post(f"{TELEGRAM_API}/sendMessage", data=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def tg_edit_message(chat_id: int, message_id: int, text: str) -> dict:
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    r = requests.post(f"{TELEGRAM_API}/editMessageText", data=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def tg_answer_callback(callback_query_id: str, text: str = "") -> None:
    payload = {"callback_query_id": callback_query_id, "text": text}
    requests.post(f"{TELEGRAM_API}/answerCallbackQuery", data=payload, timeout=20)


def send_draft_to_admin() -> None:
    values = get_sheet_values()
    previous = load_state()
    text = build_message(values, previous)
    tg_send_message(ADMIN_CHAT_ID, text, reply_markup=confirm_keyboard())
