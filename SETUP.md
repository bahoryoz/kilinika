# 🏥 Klinika Navbati - To'liq Setup Guide

## Tez boshlash (Quick Start)

### Terminal 1 - Django Server

```powershell
cd C:\Users\user\Music\kilinika_navbati
.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py shell < seed_data.py
python manage.py createsuperuser
python manage.py runserver
```

### Terminal 2 - Telegram Bot

Avval `.env` faylida `BOT_TOKEN` qo'yish kerak:

```powershell
cd C:\Users\user\Music\kilinika_navbati
.venv\Scripts\Activate.ps1
python -m botapp.bot
```

---

## Batafsil Setup

### 1. Virtual Environment Yaratish

```powershell
cd C:\Users\user\Music\kilinika_navbati
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Dependencies O'rnatish

```powershell
pip install -r requirements.txt
```

### 3. .env Faylini Sozlash

```powershell
# Copy template
Copy-Item .env.example .env
```

`.env` faylini oching va quyidagini to'ldiring:

```env
SECRET_KEY=dev-secret-key-for-local-clinic
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=sqlite
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
BOT_API_BASE_URL=http://localhost:8000/api
```

### 4. Database Migration

```powershell
python manage.py migrate
```

### 5. Demo Ma'lumotlar Yaratish

```powershell
python manage.py shell < seed_data.py
```

Bu 3 ta shifokor va 7 kun uchun jadval va slotlarni yaratadi.

### 6. Admin Akkaunti Yaratish (Optional)

```powershell
python manage.py createsuperuser
```

### 7. Django Server Ishga Tushirish

```powershell
python manage.py runserver
```

Ochiq:
- Admin panel: http://localhost:8000/admin/
- API root: http://localhost:8000/api/
- Specialities: http://localhost:8000/api/specialities/
- Doctors: http://localhost:8000/api/doctors/

### 8. Telegram Bot Ishga Tushirish

Yana boshqa terminal oyna ochib:

```powershell
cd C:\Users\user\Music\kilinika_navbati
.venv\Scripts\Activate.ps1
python -m botapp.bot
```

Bot console da "Bot ishga tushmoqda..." xabarini ko'rsatadi.

---

## Telegram Bot Token Olish

1. @BotFather ga xabar yuboring: https://t.me/BotFather
2. `/newbot` buyrug'i berish
3. Bot nomini kiriting (masalan: "Klinika Navbati Bot")
4. Username kiriting (masalan: "clinic_navbati_bot")
5. BotFather sizga token beradi (masalan: `123456789:ABCdef...`)
6. `.env` faylida `BOT_TOKEN=123456789:ABCdef...` qiling
7. Bot restart qiling

---

## Bot Oqimi

1. `/start` yoki "🏥 Navbat olish" tugmasini bosing
2. Yo'nalishni tanlang (Terapevt, Stomatolog, Kardiolog)
3. Shifokorni tanlang
4. Sanani tanlang (bu haftaga bo'sh kunlar)
5. Vaqtni tanlang (ish vaqti ichidagi slotlar)
6. Shikoyatni yozing (yoki o'tkazib yuborish)
7. Tasdiqlang
8. Navbat band bo'ladi ✅

---

## API Endpointlari (Testing)

```bash
# Yo'nalishlar
GET /api/specialities/

# Shifokorlar
GET /api/doctors/
GET /api/doctors/?speciality=1

# Slotlar
GET /api/slots/?doctor=1&date=2026-09-15

# Mavjud kunlar
GET /api/slots/available-days/?doctor=1
```

---

## Muammolar va Yechimlar

### Bot: "Unauthorized: invalid token specified"

**Sabab:** `.env` faylida `BOT_TOKEN` bo'sh yoki noto'g'ri.

**Yechim:** 
1. @BotFather dan yangi token oling
2. `.env` faylida to'liq token qo'yish

### Bot: "Connection refused" (API ga ulanmadi)

**Sabab:** Django server ishlamayapti.

**Yechim:** 
1. Terminal 1 da Django server ishga tushiring
2. `python manage.py runserver` buyrug'ini bajaring

### Django: "No such table: clinic_xxx"

**Sabab:** Migratsiya qilmagan.

**Yechim:** 
```powershell
python manage.py migrate
```

### Bot: "Bu yo'nalishdagi shifokorlar mavjud emas"

**Sabab:** Demo ma'lumotlar yaratilmagan.

**Yechim:** 
```powershell
python manage.py shell < seed_data.py
```

---

## Loyiha Fayl Tuzilmasi

```
kilinika_navbati/
├── config/              # Django settings
├── accounts/            # User modeli
├── clinic/              # Clinic modeli, API
│   ├── models.py        # Database models
│   ├── views.py         # DRF ViewSets
│   ├── serializers.py   # Serializers
│   ├── urls.py          # API routes
│   └── services.py      # Business logic
├── botapp/              # Telegram bot
│   ├── bot.py          # Bot handlers va FSM
│   └── api_client.py   # Bot → API client
├── .env                 # Environment variables
├── seed_data.py         # Demo data script
├── manage.py            # Django management
└── requirements.txt     # Dependencies
```

---

## Keyingi Qadamlar

1. **Haqiqiy Telegram ID bilan autentifikatsiya** — token-ga almashish
2. **Appointment band qilishni API orqali** — hozir stub sifatida
3. **Navbatlarni ko'rish va bekor qilish** — API'dan real ma'lumotlarni olib kelish
4. **Eslatma yuborish** — qabul vaqtidan 1 kun oldin
5. **Admin panel** — shifokor va registrator bilan ishlash

---

## Support

Muammolar bo'lsa, `python manage.py check` buyrug'iga qo'ying yoki log faylni ko'ring.
