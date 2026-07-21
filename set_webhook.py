"""
Bu skriptni FAQAT BIR MARTA, Web Service Render'da ishga tushgandan keyin qo'lda ishga
tushirasiz — Telegram'ga "endi xabarlarni shu manzilga yubor" deb aytish uchun.

Ishlatish: WEBHOOK_URL muhit o'zgaruvchisini o'rnatib, python set_webhook.py deb yozing.
Masalan: WEBHOOK_URL=https://kassa-bot-web.onrender.com/webhook python set_webhook.py
"""

import os

import requests

from common import BOT_TOKEN

WEBHOOK_URL = os.environ["WEBHOOK_URL"]

r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    data={"url": WEBHOOK_URL},
)
print(r.json())
