# Klinika navbati

Bu loyiha kichik klinikada bemorlar uchun Telegram bot orqali navbat olish tizimini ko'radi. Sistema Django + DRF + PostgreSQL + aiogram 3 asosida yaratilgan.

## Tekshiruv

- `python manage.py check` — Django konfiguratsiyasi va app sozlamalari tekshirildi.
- `python manage.py makemigrations` — migration fayllari yaratilishi tekshirildi.
- PostgreSQL serverini ishga tushirish kerak: loyiha PostgreSQL bilan ishlaydi, lokal kompyuterda service mavjud bo'lmaganligi sababli DB ishlatib bo'lmadi.

## O'rnatish

1. Virtual environment yarating:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Bog'liqliklarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` faylini sozlang:
   ```bash
   copy .env.example .env
   ```
4. PostgreSQL ma'lumotlar bazasini yarating va `DB_*` parametrlarini to'ldiring.
5. Migratsiyalarni yaratish:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Superuser yaratish:
   ```bash
   python manage.py createsuperuser
   ```
7. Botni ishga tushirish:
   ```bash
   python manage.py runserver
   python -m botapp.bot
   ```
