#!/bin/bash
# Loyiha to'liq setup va run script

echo "🏥 Klinika navbati - Setup va ishga tushirish"
echo "==========================================="

# 1. Virtual environment aktivatsiya
echo "1️⃣ Virtual environment aktivatsiya..."
if [ -d ".venv" ]; then
    source .venv/Scripts/activate
else
    echo "❌ .venv topilmadi. Avval 'python -m venv .venv' jarayonini bajaring"
    exit 1
fi

# 2. Database migratsiya
echo ""
echo "2️⃣ Database migratsiya..."
python manage.py migrate

# 3. Demo ma'lumotlar yaratish
echo ""
echo "3️⃣ Demo ma'lumotlar yaratish..."
python manage.py shell < seed_data.py

# 4. Superuser yaratish (optional)
echo ""
echo "4️⃣ Superuser (admin) yaratish opsiyonal. Xohlasangiz, quyidagini bajaring:"
echo "   python manage.py createsuperuser"

# 5. Django server ishga tushirish
echo ""
echo "5️⃣ Django server ishga tushmoqda..."
echo "   Admin panel: http://localhost:8000/admin"
echo "   API root: http://localhost:8000/api/"
python manage.py runserver
