# Kassa Hisobot Bot — Render'da BEPUL joylashtirish

Bot ikkita bo'lakdan iborat:
- **Cron Job** — har kuni 06:00da (Toshkent vaqti) ishga tushib, sizga hisobotni yuboradi
- **Web Service** — doim tinch turadi, siz ✅/✏️/❌ tugmalarini bosganingizda ishlaydi

Ikkalasi ham Render'ning bepul tarifida ishlaydi.

---

## 1-QADAM: Google Sheets ruxsatini yangilash

Avvalgi bosqichda service account'ga "Читатель" (Viewer) huquqi berilgan edi.
Endi uni **"Редактор"** (Editor) ga o'zgartiring:
1. Google Sheets'da **Настройки доступа** ni oching
2. Service account emailingiz yonidagi huquqni "Читатель"dan **"Редактор"**ga o'zgartiring
3. Saqlang

(Bot avtomatik ravishda jadvalga "BotState" degan yashirin varaq qo'shib, kecha/bugungi
qiymatlarni o'sha yerda saqlaydi — o'zingiz hech narsa yaratishingiz shart emas.)

---

## 2-QADAM: Kodni GitHub'ga joylash

Render GitHub repozitoriyidan kodni oladi. Agar GitHub akkauntingiz bo'lmasa:
1. https://github.com da ro'yxatdan o'ting (bepul)
2. Yangi repository yarating (masalan `kassa-bot`), **Private** qilib qo'yish tavsiya etiladi
3. Men bergan fayllarni (common.py, webapp.py, send_daily.py, set_webhook.py, requirements.txt)
   shu repoga yuklang — GitHub saytida **"Add file → Upload files"** orqali sudrab tashlashingiz mumkin
4. **`service_account.json` faylini GitHub'ga YUKLAMANG** — bu maxfiy fayl, uni faqat Render sozlamalariga (3-qadamda) joylaymiz

---

## 3-QADAM: Render'da akkaunt va servislar

1. https://render.com da ro'yxatdan o'ting (GitHub akkauntingiz bilan kirsangiz bo'ladi)
2. Dashboard'da **"New +"** → **"Web Service"** ni tanlang
3. GitHub repongizni tanlang (`kassa-bot`)
4. Sozlamalar:
   - **Name**: `kassa-bot-web`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn webapp:app`
   - **Instance Type**: **Free**
5. Pastroqda **"Environment Variables"** bo'limida `.env.example` fayldagi barcha o'zgaruvchilarni
   birma-bir qo'shing (TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID, GROUP_CHAT_ID, SPREADSHEET_ID, SHEET_NAME,
   TIMEZONE)
6. `SERVICE_ACCOUNT_JSON` uchun: `service_account.json` faylini matn muharririda oching, **butun
   ichidagi matnni** nusxalab, shu muhit o'zgaruvchisining qiymati sifatida joylang
7. **"Create Web Service"** bosing — bir necha daqiqada tayyor bo'ladi
8. Tayyor bo'lgach, yuqorida sizga berilgan manzilni ko'rasiz, masalan:
   `https://kassa-bot-web.onrender.com` — shu manzilni eslab qoling

### Webhook'ni ulash (bir martalik amal)

O'z kompyuteringizda terminal orqali:
```
cd kassa_bot
pip install -r requirements.txt
set TELEGRAM_BOT_TOKEN=sizning_tokeningiz
set WEBHOOK_URL=https://kassa-bot-web.onrender.com/webhook
python set_webhook.py
```
(Mac/Linux'da `set` o'rniga `export` yozasiz)

Natijada `{"ok":true,...}` chiqsa — muvaffaqiyatli ulandi.

### Cron Job qo'shish

1. Render Dashboard'da **"New +"** → **"Cron Job"**
2. Xuddi shu GitHub repongizni tanlang
3. Sozlamalar:
   - **Name**: `kassa-bot-daily`
   - **Build Command**: `pip install -r requirements.txt`
   - **Command**: `python send_daily.py`
   - **Schedule**: `0 1 * * *`   ← bu UTC bo'yicha 01:00, ya'ni Toshkent vaqti bilan **06:00**
   - **Instance Type**: **Free**
4. Xuddi shu Environment Variable'larni bu yerga ham qo'shing (Web Service'dagi bilan bir xil)
5. **"Create Cron Job"** bosing

---

## Tayyor!

Endi har kuni soat 06:00da (Toshkent vaqti) botingiz sizga hisobotni yuboradi.
Tugmalar orqali tasdiqlaysiz — u guruhga avtomatik ketadi.

Istalgan vaqt qo'lda so'rash uchun botga `/report` deb yozing.

### Muammo chiqsa
- Render Dashboard'da har bir servis ichida **"Logs"** bo'limi bor — xatolik matni shu yerda ko'rinadi, uni menga nusxalab yuboring
- Eng ko'p uchraydigan xato: Environment Variable noto'g'ri yozilgan yoki `SERVICE_ACCOUNT_JSON` to'liq nusxalanmagan
