# Kassa Hisobot Bot — Render'da BEPUL joylashtirish (yangilangan)

Render 2026-yil aprelida siyosatini o'zgartirdi — endi **Cron Job bepul emas**.
Shuning uchun sxema soddalashtirildi: faqat **bitta Render Web Service** (bepul) ishlatamiz,
va har kuni soat 06:00da uni "uyg'otish" uchun tashqi **bepul** xizmat — cron-job.org — dan
foydalanamiz.

---

## 1-QADAM: Google Sheets ruxsati

Service account'ga **"Редактор"** (Editor) huquqi berilganini tekshiring (avvalgi bosqichda
qilingan bo'lsa, bu qadam kerak emas).

---

## 2-QADAM: Kodni GitHub'ga yuklash

Fayllar: `common.py`, `webapp.py`, `set_webhook.py`, `requirements.txt`
(`service_account.json`ni GitHub'ga yuklamang — maxfiy).

---

## 3-QADAM: Render'da Web Service

1. Render Dashboard → **"New +" → "Web Service"**
2. GitHub repongizni ulang (`kassa-bot`)
3. Sozlamalar:
   - **Name**: `kassa-bot-web`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn webapp:app`
   - **Instance Type**: **Free**
4. **Environment Variables** bo'limida qo'shing:

| Key | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | bot tokeningiz |
| `ADMIN_CHAT_ID` | sizning chat ID |
| `GROUP_CHAT_ID` | guruh chat ID |
| `SPREADSHEET_ID` | jadval ID |
| `SHEET_NAME` | `Cash Flow` |
| `TIMEZONE` | `Asia/Tashkent` |
| `SERVICE_ACCOUNT_JSON` | service_account.json faylining butun matni |
| `TRIGGER_SECRET` | o'zingiz o'ylab topgan maxfiy so'z, masalan `kassa2026sirli` |

5. **"Create Web Service"** bosing, tugagach manzilingizni oling, masalan:
   `https://kassa-bot-web.onrender.com`

---

## 4-QADAM: Webhook'ni ulash (bir martalik)

O'z kompyuteringizda terminalda:
```
cd kassa_bot
pip install -r requirements.txt
set TELEGRAM_BOT_TOKEN=sizning_tokeningiz
set WEBHOOK_URL=https://kassa-bot-web.onrender.com/webhook
python set_webhook.py
```
`{"ok":true,...}` chiqsa — muvaffaqiyatli.

---

## 5-QADAM: Har kuni avtomatik ishga tushirish (cron-job.org, bepul)

1. https://cron-job.org da ro'yxatdan o'ting (bepul, email bilan)
2. **"Create cronjob"** bosing
3. **Title**: `Kassa daily report`
4. **URL**: 
   ```
   https://kassa-bot-web.onrender.com/trigger-daily?token=kassa2026sirli
   ```
   (`token=` qismiga Render'da qo'ygan `TRIGGER_SECRET` qiymatingizni yozing)
5. **Schedule**: Har kuni, vaqt: **01:00** (bu UTC — Toshkent vaqti bilan 06:00 bo'ladi)
6. **Save** bosing

---

## Tayyor!

Har kuni soat 06:00da (Toshkent) cron-job.org sizning Render xizmatingizni "uyg'otadi",
u jadvaldan o'qib sizga hisobot yuboradi. Tugmalar orqali tasdiqlaysiz — guruhga ketadi.

Qo'lda so'rash uchun botga `/report` deb yozing.

### Eslatma
Bepul Render Web Service 15 daqiqa harakatsiz tursa "uxlab qoladi" — birinchi so'rov kelganda
(cron-job.org yoki sizning tugma bosishingiz) 30-50 soniya kechikish bo'lishi mumkin, bu normal.

### Muammo chiqsa
Render Dashboard → xizmatingiz → **"Logs"** bo'limidagi xatolik matnini menga yuboring.
