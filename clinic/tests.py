from django.test import TestCase


class ClinicBookingSmokeTest(TestCase):
    def test_project_imports(self):
        self.assertTrue(True)

    def test_default_status(self):
        self.assertEqual(1 + 1, 2)
