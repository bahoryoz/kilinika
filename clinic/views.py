import datetime as dt

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import SlotConflictError
from .models import Appointment, Doctor, Schedule, Slot, Speciality, Visit
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    DoctorSerializer,
    ScheduleSerializer,
    SlotSerializer,
    SpecialitySerializer,
    VisitSerializer,
)
from .services import generate_slots_for_schedule, get_available_days_for_doctor


class SpecialityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Speciality.objects.filter(is_active=True)
    serializer_class = SpecialitySerializer
    permission_classes = [IsAuthenticated]


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.select_related('user', 'speciality').all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['speciality', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.role == 'doctor':
            return qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'registrator':
            raise ValidationError({'detail': "Faqat registrator yangi shifokor qo'shishi mumkin."})
        doctor_user = serializer.validated_data['user']
        doctor_user.role = 'doctor'
        doctor_user.save(update_fields=['role'])
        serializer.save()


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related('doctor__user', 'doctor__speciality')
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['doctor', 'date']

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.role == 'doctor':
            return qs.filter(doctor__user=self.request.user)
        return qs

    @action(detail=True, methods=['post'])
    def generate_slots(self, request, pk=None):
        if request.user.role != 'registrator':
            raise ValidationError({'detail': 'Faqat registrator slot generatsiya qila oladi.'})
        schedule = self.get_object()
        slots = generate_slots_for_schedule(schedule)
        return Response({'created': len(slots)})


class SlotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Slot.objects.select_related('doctor__user', 'doctor__speciality').filter(is_available=True)
        doctor = self.request.query_params.get('doctor')
        date = self.request.query_params.get('date')
        if doctor:
            qs = qs.filter(doctor_id=doctor)
        if date:
            qs = qs.filter(date=date)
        return qs

    @action(detail=False, methods=['get'], url_path='available-days')
    def available_days(self, request):
        doctor_id = request.query_params.get('doctor')
        if not doctor_id:
            return Response({'detail': 'doctor param required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(get_available_days_for_doctor(doctor_id))


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('slot__doctor__user', 'patient')
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['slot__date', 'slot__doctor', 'status']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.role == 'patient':
            return qs.filter(patient=user)
        if user.role == 'doctor':
            return qs.filter(slot__doctor__user=user)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = AppointmentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            appointment = serializer.save()
        except SlotConflictError as exc:
            raise exc
        except Exception as exc:
            if 'slot' in str(exc):
                raise ValidationError({'detail': 'Bu vaqt band bo\'lib qolgan.'})
            raise exc
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if request.user.role not in ('patient', 'registrator'):
            raise ValidationError({'detail': 'Faqat bemor yoki registrator bekor qila oladi.'})
        if request.user.role == 'patient' and appointment.patient_id != request.user.id:
            raise ValidationError({'detail': 'Siz faqat o\'zingizning navbatini bekor qila olasiz.'})

        slot_dt = dt.datetime.combine(appointment.slot.date, appointment.slot.start_time)
        if timezone.now() >= slot_dt - dt.timedelta(hours=2):
            raise ValidationError({'detail': 'Navbatni bekor qilish uchun qabul vaqtidan kamida 2 soat oldin bo\'lishi kerak.'})

        with transaction.atomic():
            appointment.status = 'cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.save(update_fields=['status', 'cancelled_at'])
            appointment.slot.is_available = True
            appointment.slot.save(update_fields=['is_available'])

        return Response({'detail': 'Navbat bekor qilindi.'})

    @action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        if request.user.role != 'doctor':
            raise ValidationError({'detail': 'Faqat shifokor statuse o\'zgartirishi mumkin.'})
        new_status = request.data.get('status')
        if new_status not in ['arrived', 'missed']:
            raise ValidationError({'detail': 'Status faqat keldi yoki kelmadi bo\'lishi kerak.'})
        appointment = self.get_object()
        appointment.status = new_status
        appointment.save(update_fields=['status'])
        return Response({'detail': f'Status {new_status} ga o\'zgartirildi.'})


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.select_related('appointment__patient', 'appointment__slot__doctor__user')
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.role == 'doctor':
            return qs.filter(appointment__slot__doctor__user=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        if request.user.role != 'doctor':
            raise ValidationError({'detail': 'Faqat shifokor qabul natijasini yozishi mumkin.'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = serializer.save()
        appointment = visit.appointment
        appointment.status = 'arrived'
        appointment.save(update_fields=['status'])
        return Response(self.get_serializer(visit).data, status=status.HTTP_201_CREATED)


class DailyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'registrator':
            raise ValidationError({'detail': 'Faqat registrator hisobot ko\'ra oladi.'})
        today = timezone.localdate()
        data = (
            Appointment.objects.filter(slot__date=today)
            .values('slot__doctor__id', 'slot__doctor__user__username')
            .annotate(total=Count('id'), income=Sum('slot__doctor__price'))
            .order_by('slot__doctor__user__username')
        )
        return Response(list(data))


class NoShowReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'registrator':
            raise ValidationError({'detail': 'Faqat registrator hisobot ko\'ra oladi.'})
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            return Response({'detail': 'start_date va end_date talab qilinadi.'}, status=status.HTTP_400_BAD_REQUEST)

        data = (
            Appointment.objects.filter(status='missed', slot__date__range=[start_date, end_date])
            .values('slot__doctor__user__username')
            .annotate(count=Count('id'))
            .order_by('slot__doctor__user__username')
        )
        return Response(list(data))


class MyAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'patient':
            return Response({'detail': 'Bemor uchun faqat o\'zingizning navbatlarini ko\'rish mumkin.'}, status=status.HTTP_403_FORBIDDEN)
        qs = Appointment.objects.filter(patient=request.user).select_related('slot__doctor__user', 'slot__doctor__speciality')
        return Response(AppointmentSerializer(qs, many=True).data)
