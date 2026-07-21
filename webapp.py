"""
Render Web Service shu faylni doim ishlab turadigan holatda ishga tushiradi.
Vazifasi: Telegram'dan kelgan tugma bosishlarni (✅/✏️/❌) va matn xabarlarni qabul qilish.
"""

import os

from flask import Flask, request

from common import (
    ADMIN_CHAT_ID,
    GROUP_CHAT_ID,
    build_message,
    confirm_keyboard,
    get_sheet_values,
    load_state,
    save_state,
    tg_answer_callback,
    tg_edit_message,
    tg_send_message,
)

app = Flask(__name__)

# Admin "Tahrirlash" tugmasini bosgach, keyingi xabarini kutayotganini eslab turish uchun
awaiting_edit: set[int] = set()


@app.route("/", methods=["GET"])
def health():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True) or {}

    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_message(update["message"])

    return "OK", 200


def handle_callback(cq: dict) -> None:
    user_id = cq["from"]["id"]
    data = cq.get("data")
    message = cq["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    original_text = message.get("text", "")

    tg_answer_callback(cq["id"])

    if user_id != ADMIN_CHAT_ID:
        return

    if data == "confirm":
        tg_send_message(GROUP_CHAT_ID, original_text)
        try:
            save_state(get_sheet_values())
        except Exception as e:
            tg_send_message(ADMIN_CHAT_ID, f"⚠️ Holatni saqlashda xatolik: {e}")
        tg_edit_message(chat_id, message_id, original_text + "\n\n✅ Guruhga yuborildi.")

    elif data == "edit":
        awaiting_edit.add(user_id)
        tg_edit_message(chat_id, message_id, original_text + "\n\n✏️ Yangi matnni shu chatga yozib yuboring:")

    elif data == "cancel":
        tg_edit_message(chat_id, message_id, original_text + "\n\n❌ Bekor qilindi.")


def handle_message(msg: dict) -> None:
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    if text == "/start":
        tg_send_message(chat_id, f"Salom! Sizning chat ID: {chat_id}")
        return

    if text == "/report":
        if chat_id != ADMIN_CHAT_ID:
            return
        try:
            values = get_sheet_values()
            previous = load_state()
            draft = build_message(values, previous)
            tg_send_message(ADMIN_CHAT_ID, draft, reply_markup=confirm_keyboard())
        except Exception as e:
            tg_send_message(ADMIN_CHAT_ID, f"⚠️ Xatolik: {e}")
        return

    if chat_id == ADMIN_CHAT_ID and chat_id in awaiting_edit:
        awaiting_edit.discard(chat_id)
        tg_send_message(chat_id, text, reply_markup=confirm_keyboard())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
