# Phase 4D — compliance daily jobs command

from datetime import date, timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from delivery.compliance_constants import DocumentStatus, DocumentType
from delivery.compliance_service import create_document, mark_verified
from delivery.models import Driver, DriverVehicle, LegalDocument, Vehicle


class RunComplianceDailyJobsTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff_daily', password='pass', is_staff=True)
        self.driver_user = User.objects.create_user(
            username='driver_daily',
            password='pass',
            email='daily.driver@example.com',
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            first_name='Daily',
            last_name='Driver',
            phone_number='555-0411',
            license_number='DL-DY-001',
            license_issuing_region='CA-BC',
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='DY001',
            make='Ford',
            model='F-150',
            year=2022,
            vin='1FTDYTEST0000001',
            capacity=1200,
            capacity_unit='kg',
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@test.local',
    )
    def test_run_compliance_daily_jobs_expires_and_reminds(self):
        expired = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.VEHICLE_REGISTRATION,
                'expiry_date': date.today() - timedelta(days=1),
            },
        )
        mark_verified(self.staff, expired.id)

        remind = create_document(
            self.staff,
            driver=self.driver,
            data={
                'document_type': DocumentType.DRIVER_LICENSE,
                'expiry_date': date.today() + timedelta(days=30),
            },
        )
        mark_verified(self.staff, remind.id)

        out = StringIO()
        call_command('run_compliance_daily_jobs', stdout=out)
        output = out.getvalue()

        expired.refresh_from_db()
        self.assertEqual(expired.status, DocumentStatus.EXPIRED)
        self.assertIn('Marked 1 document(s) as EXPIRED', output)
        self.assertIn('Sent 1 (30-day)', output)

        remind.refresh_from_db()
        self.assertIsNotNone(remind.expiry_reminder_30_sent_at)
