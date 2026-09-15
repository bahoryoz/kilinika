from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet,
    DailyReportView,
    DoctorViewSet,
    MyAppointmentsView,
    NoShowReportView,
    ScheduleViewSet,
    SlotViewSet,
    SpecialityViewSet,
    VisitViewSet,
)

router = DefaultRouter()
router.register(r'specialities', SpecialityViewSet, basename='specialities')
router.register(r'doctors', DoctorViewSet, basename='doctors')
router.register(r'schedules', ScheduleViewSet, basename='schedules')
router.register(r'slots', SlotViewSet, basename='slots')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'visits', VisitViewSet, basename='visits')

urlpatterns = [
    path('', include(router.urls)),
    path('appointments/my/', MyAppointmentsView.as_view(), name='my-appointments'),
    path('reports/daily/', DailyReportView.as_view(), name='daily-report'),
    path('reports/no-show/', NoShowReportView.as_view(), name='no-show-report'),
]
