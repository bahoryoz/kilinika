from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from accounts.models import User
from .exceptions import SlotConflictError
from .models import Appointment, Doctor, Schedule, Slot, Speciality, Visit


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ['id', 'name', 'is_active']


class DoctorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    speciality = serializers.PrimaryKeyRelatedField(queryset=Speciality.objects.all())
    doctor_name = serializers.SerializerMethodField()
    speciality_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'doctor_name', 'speciality', 'speciality_name', 'room', 'slot_minutes', 'price', 'is_active']

    def get_doctor_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_speciality_name(self, obj):
        return obj.speciality.name

    def validate_user(self, value):
        if value.role != 'doctor':
            raise serializers.ValidationError("Shifokor yaratilishi uchun user roli \"shifokor\" bo'lishi kerak.")
        return value


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'date', 'start_time', 'end_time', 'break_start', 'break_end']

    def validate(self, attrs):
        if attrs.get('date') and attrs['date'] < timezone.localdate():
            raise serializers.ValidationError({'date': "O'tgan sanaga jadval kiritib bo'lmaydi."})
        return attrs


class SlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_room = serializers.SerializerMethodField()

    class Meta:
        model = Slot
        fields = ['id', 'doctor', 'doctor_name', 'doctor_room', 'date', 'start_time', 'end_time', 'is_available']

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name() or obj.doctor.user.username

    def get_doctor_room(self, obj):
        return obj.doctor.room


class AppointmentSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(read_only=True)
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'slot', 'patient', 'patient_name', 'doctor_name', 'status', 'complaint', 'created_at', 'cancelled_at', 'reminder_sent_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def get_doctor_name(self, obj):
        return obj.slot.doctor.user.get_full_name() or obj.slot.doctor.user.username


class AppointmentCreateSerializer(serializers.ModelSerializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=Slot.objects.all())
    patient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Appointment
        fields = ['slot', 'patient', 'complaint']

    def validate(self, attrs):
        request = self.context.get('request')
        patient = request.user if request and request.user.is_authenticated else None
        if patient is None:
            raise serializers.ValidationError({'detail': 'Bemorni aniqlash mumkin emas.'})

        slot = attrs['slot']
        if slot.date < timezone.localdate():
            raise serializers.ValidationError({'detail': "O'tgan sanaga navbat olish mumkin emas."})
        if not slot.is_available:
            raise serializers.ValidationError({'detail': 'Bu vaqt band bo\'lib qolgan.'})

        existing = Appointment.objects.filter(
            patient=patient,
            slot__date=slot.date,
            slot__doctor=slot.doctor,
            status__in=['booked', 'arrived'],
        ).exists()
        if existing:
            raise serializers.ValidationError({'detail': 'Bir kunda bir shifokorga faqat bitta faol navbat bo\'lishi mumkin.'})

        attrs['patient'] = patient
        return attrs

    def create(self, validated_data):
        slot = validated_data['slot']
        patient = validated_data['patient']
        with transaction.atomic():
            slot_obj = Slot.objects.select_for_update().get(pk=slot.pk)
            if not slot_obj.is_available:
                raise SlotConflictError()

            existing = Appointment.objects.filter(
                patient=patient,
                slot__date=slot_obj.date,
                slot__doctor=slot_obj.doctor,
                status__in=['booked', 'arrived'],
            ).exists()
            if existing:
                raise serializers.ValidationError({'detail': 'Bir kunda bir shifokorga faqat bitta faol navbat bo\'lishi mumkin.'})

            appointment = Appointment.objects.create(
                slot=slot_obj,
                patient=patient,
                complaint=validated_data.get('complaint', ''),
            )
            slot_obj.is_available = False
            slot_obj.save(update_fields=['is_available'])
            return appointment


class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = ['id', 'appointment', 'diagnosis', 'recommendation', 'created_at']


class UpdateAppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']
