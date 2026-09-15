from django.contrib import admin

from .models import Appointment, Doctor, Schedule, Slot, Speciality, Visit


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'speciality', 'room', 'slot_minutes', 'price', 'is_active')
    list_filter = ('speciality', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'room')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'break_start', 'break_end')
    list_filter = ('doctor', 'date')
    search_fields = ('doctor__user__username', 'doctor__user__first_name', 'doctor__user__last_name')


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('doctor', 'date', 'is_available')
    search_fields = ('doctor__user__username',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'slot', 'status', 'created_at', 'cancelled_at')
    list_filter = ('status', 'slot__date')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'complaint')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'diagnosis', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('diagnosis', 'recommendation', 'appointment__patient__username')
