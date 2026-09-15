import datetime as dt
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Appointment, Slot


def generate_slots_for_schedule(schedule):
    with transaction.atomic():
        Slot.objects.filter(doctor=schedule.doctor, date=schedule.date).exclude(appointment__isnull=False).delete()

        current = dt.datetime.combine(schedule.date, schedule.start_time)
        end = dt.datetime.combine(schedule.date, schedule.end_time)
        break_start = dt.datetime.combine(schedule.date, schedule.break_start) if schedule.break_start else None
        break_end = dt.datetime.combine(schedule.date, schedule.break_end) if schedule.break_end else None

        slots = []
        while current + dt.timedelta(minutes=schedule.doctor.slot_minutes) <= end:
            slot_end = current + dt.timedelta(minutes=schedule.doctor.slot_minutes)
            if break_start and break_end:
                if not (slot_end <= break_start or current >= break_end):
                    current = slot_end
                    continue

            slot, _ = Slot.objects.update_or_create(
                doctor=schedule.doctor,
                date=schedule.date,
                start_time=current.time(),
                defaults={'end_time': slot_end.time(), 'is_available': True},
            )
            slots.append(slot)
            current = slot_end

        return slots


def get_available_days_for_doctor(doctor_id, days=14):
    today = timezone.localdate()
    dates = (
        Slot.objects.filter(doctor_id=doctor_id, is_available=True, date__gte=today, date__lte=today + timedelta(days=days))
        .values_list('date', flat=True)
        .distinct()
    )
    return [{'date': item.isoformat()} for item in dates]


def mark_no_show_appointments():
    today = timezone.localdate()
    Appointment.objects.filter(status='booked', slot__date__lt=today).update(status='missed')
    return True
