"""
Render Cron Job shu faylni har kuni bir marta ishga tushiradi.
Vazifasi: jadvaldan bugungi qiymatlarni o'qib, adminga tasdiqlash uchun yuborish.
"""

from common import send_draft_to_admin

if __name__ == "__main__":
    send_draft_to_admin()
    print("Hisobot adminga yuborildi.")
