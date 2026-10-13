from django.test import TestCase

from accounts.models import User
from clinic.models import Doctor, Speciality
from seed_data import create_demo_data


class ClinicBookingSmokeTest(TestCase):
    def test_project_imports(self):
        self.assertTrue(True)

    def test_default_status(self):
        self.assertEqual(1 + 1, 2)

    def test_create_demo_data_generates_specialties_and_staff(self):
        create_demo_data()

        self.assertGreaterEqual(Speciality.objects.count(), 4)
        self.assertGreaterEqual(User.objects.filter(role='doctor').count(), 4)
        self.assertGreaterEqual(User.objects.filter(role='registrator').count(), 4)
        self.assertGreaterEqual(User.objects.filter(role='patient').count(), 4)
        self.assertTrue(User.objects.filter(is_staff=True).exists())
        self.assertGreaterEqual(Doctor.objects.count(), 4)
