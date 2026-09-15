import datetime as dt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Speciality(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='doctor_profile')
    speciality = models.ForeignKey('Speciality', on_delete=models.PROTECT, related_name='doctors')
    room = models.CharField(max_length=20)
    slot_minutes = models.PositiveSmallIntegerField(default=20)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f'{full_name} / {self.speciality.name}'


class Schedule(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('doctor', 'date')
        constraints = [
            models.CheckConstraint(check=Q(end_time__gt=F('start_time')), name='schedule_end_after_start'),
        ]
        ordering = ['date', 'start_time']

    def clean(self):
        if self.date < timezone.localdate():
            raise ValidationError({'date': "O'tgan sanaga jadval kiritib bo'lmaydi."})
        if self.break_start and self.break_end and self.break_start >= self.break_end:
            raise ValidationError({'break_start': "Tanaffus boshlanishi tugashidan oldin bo'lishi kerak."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.doctor} - {self.date}'


class Slot(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='slots')
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        indexes = [models.Index(fields=['doctor', 'date', 'is_available'])]
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.doctor} | {self.date} {self.start_time}'


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Band'),
        ('arrived', 'Keldi'),
        ('missed', 'Kelmadi'),
        ('cancelled', 'Bekor'),
    )

    slot = models.OneToOneField('Slot', on_delete=models.PROTECT, related_name='appointment')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='appointments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    complaint = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['slot__date', 'slot__start_time']

    def __str__(self):
        return f'{self.patient} -> {self.slot}'


class Visit(models.Model):
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE, related_name='visit')
    diagnosis = models.TextField()
    recommendation = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Visit for {self.appointment.patient}'
