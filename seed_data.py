"""Demo ma'lumotlarini yaratish uchun modul."""

from datetime import time, timedelta

from accounts.models import User
from clinic.models import Doctor, Schedule, Slot, Speciality
from clinic.services import generate_slots_for_schedule
from django.utils import timezone


def _create_or_update_user(username, password, first_name, last_name, email, role, phone, is_staff=False, is_superuser=False):
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.role = role
    user.phone = phone
    user.is_staff = is_staff or role == 'registrator'
    user.is_superuser = is_superuser
    user.is_active = True
    user.save()
    return user


def create_demo_data():
    print("🔄 Demo ma'lumotlar yaratilmoqda...")

    speciality_names = [
        'Terapevt',
        'Stomatolog',
        'Kardiolog',
        'Pulmonolog',
    ]
    specialties = {}
    for name in speciality_names:
        speciality, _ = Speciality.objects.get_or_create(name=name)
        specialties[name] = speciality

    admin_user = _create_or_update_user(
        username='admin',
        password='admin123',
        first_name='Admin',
        last_name='Sistem',
        email='admin@clinic.uz',
        role='registrator',
        phone='+998900000001',
        is_staff=True,
        is_superuser=True,
    )

    registrators = [
        ('registrator1', 'registrator123', 'Shahzod', 'Murodov', 'reg1@clinic.uz', '+998900000002'),
        ('registrator2', 'registrator123', 'Nilufar', 'Rashidova', 'reg2@clinic.uz', '+998900000003'),
        ('registrator3', 'registrator123', 'Bekzod', 'Halimov', 'reg3@clinic.uz', '+998900000004'),
        ('registrator4', 'registrator123', 'Gulnora', 'Qodirova', 'reg4@clinic.uz', '+998900000005'),
    ]

    for username, password, first_name, last_name, email, phone in registrators:
        _create_or_update_user(username, password, first_name, last_name, email, 'registrator', phone, is_staff=True)

    doctors = [
        ('dr_alisher', 'password123', 'Alisher', 'Amin', 'alisher@clinic.uz', '+998901234567', 'Terapevt', '101', 20, 50000),
        ('dr_fatima', 'password123', 'Fatima', 'Karimova', 'fatima@clinic.uz', '+998902345678', 'Stomatolog', '202', 30, 80000),
        ('dr_aziz', 'password123', 'Aziz', 'Ahmedov', 'aziz@clinic.uz', '+998903456789', 'Kardiolog', '303', 25, 100000),
        ('dr_nodira', 'password123', 'Nodira', 'Saidova', 'nodira@clinic.uz', '+998904567890', 'Pulmonolog', '404', 35, 120000),
    ]

    doctor_profiles = []
    for username, password, first_name, last_name, email, phone, speciality_name, room, slot_minutes, price in doctors:
        user = _create_or_update_user(username, password, first_name, last_name, email, 'doctor', phone, is_staff=False)
        doctor, _ = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'speciality': specialties[speciality_name],
                'room': room,
                'slot_minutes': slot_minutes,
                'price': price,
                'is_active': True,
            },
        )
        if doctor.speciality_id != specialties[speciality_name].id:
            doctor.speciality = specialties[speciality_name]
            doctor.room = room
            doctor.slot_minutes = slot_minutes
            doctor.price = price
            doctor.is_active = True
            doctor.save()
        doctor_profiles.append(doctor)

    patients = [
        ('patient1', 'patient123', 'Jamshid', 'Jalolov', 'patient1@clinic.uz', '+998905000001'),
        ('patient2', 'patient123', 'Leyla', 'Abdullayeva', 'patient2@clinic.uz', '+998905000002'),
        ('patient3', 'patient123', 'Diyor', 'Sultanov', 'patient3@clinic.uz', '+998905000003'),
        ('patient4', 'patient123', 'Mavluda', 'Karimova', 'patient4@clinic.uz', '+998905000004'),
    ]
    for username, password, first_name, last_name, email, phone in patients:
        _create_or_update_user(username, password, first_name, last_name, email, 'patient', phone)

    today = timezone.localdate()

    for doctor in doctor_profiles:
        for day_offset in range(14):
            schedule_date = today + timedelta(days=day_offset)
            schedule, _ = Schedule.objects.get_or_create(
                doctor=doctor,
                date=schedule_date,
                defaults={
                    'start_time': time(9, 0),
                    'end_time': time(17, 0),
                    'break_start': time(12, 0),
                    'break_end': time(13, 0),
                },
            )
            generate_slots_for_schedule(schedule)

    print("✅ Yo'nalishlar yaratildi")
    print("✅ Shifokorlar, registratorlar, bemorlar va adminlar yaratildi")
    print("✅ Jadvallar va slotlar yaratildi")

    print("\n" + "=" * 60)
    print("📊 DATABASE STATISTIKA")
    print("=" * 60)
    print(f"✅ Yo'nalishlar: {Speciality.objects.count()}")
    print(f"✅ Shifokorlar: {Doctor.objects.count()}")
    print(f"✅ Registratorlar: {User.objects.filter(role='registrator').count()}")
    print(f"✅ Bemorlar: {User.objects.filter(role='patient').count()}")
    print(f"✅ Jadvallar: {Schedule.objects.count()}")
    print(f"✅ Slotlar: {Slot.objects.count()}")
    print(f"✅ Foydalanuvchilar: {User.objects.count()}")
    print("=" * 60)
    print("\nTest uchun loginlar:")
    print("  admin / admin123")
    print("  dr_alisher / password123")
    print("  registrator1 / registrator123")
    print("  patient1 / patient123")

    return {
        'specialities': list(Speciality.objects.values_list('name', flat=True)),
        'doctors': list(Doctor.objects.values_list('user__username', flat=True)),
        'registrators': list(User.objects.filter(role='registrator').values_list('username', flat=True)),
        'patients': list(User.objects.filter(role='patient').values_list('username', flat=True)),
    }


if __name__ == '__main__':
    import os

    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    create_demo_data()
