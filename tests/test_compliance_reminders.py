# Phase 4D — compliance expiry email reminders

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from delivery.compliance_constants import DocumentStatus, DocumentType
from delivery.compliance_reminder_service import (
    clear_expiry_reminder_fields,
    send_compliance_expiry_reminders,
)
from delivery.compliance_service import create_document, mark_verified
from delivery.models import Driver, DriverVehicle, LegalDocument, Vehicle


class ComplianceExpiryReminderTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff_remind',
            password='pass',
            is_staff=True,
        )
        self.driver_user = User.objects.create_user(
            username='driver_remind',
            password='pass',
            email='driver.remind@example.com',
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            first_name='Remy',
            last_name='Driver',
            phone_number='555-0410',
            license_number='DL-RM-001',
            license_issuing_region='CA-BC',
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='RM001',
            make='Ford',
            model='F-150',
            year=2022,
            vin='1FTRMTEST0000001',
            capacity=1200,
            capacity_unit='kg',
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    def _verified_driver_license(self, *, expiry: date) -> LegalDocument:
        doc = create_document(
            self.staff,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE, 'expiry_date': expiry},
        )
        return mark_verified(self.staff, doc.id)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@test.local',
    )
    def test_sends_30_day_reminder_once(self):
        today = date.today()
        expiry = today + timedelta(days=30)
        doc = self._verified_driver_license(expiry=expiry)

        result = send_compliance_expiry_reminders(as_of_date=today)
        self.assertEqual(result['sent'][30], 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('expires in 30 days', mail.outbox[0].subject)

        doc.refresh_from_db()
        self.assertIsNotNone(doc.expiry_reminder_30_sent_at)

        mail.outbox.clear()
        result_again = send_compliance_expiry_reminders(as_of_date=today)
        self.assertEqual(result_again['sent'][30], 0)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@test.local',
    )
    def test_sends_expiry_day_reminder_for_vehicle_doc(self):
        today = date.today()
        doc = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.VEHICLE_REGISTRATION,
                'expiry_date': today,
            },
        )
        mark_verified(self.staff, doc.id)

        result = send_compliance_expiry_reminders(as_of_date=today)
        self.assertEqual(result['sent'][0], 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('expires today', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['driver.remind@example.com'])

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@test.local',
    )
    def test_dry_run_does_not_send_or_update(self):
        today = date.today()
        doc = self._verified_driver_license(expiry=today + timedelta(days=14))

        result = send_compliance_expiry_reminders(as_of_date=today, dry_run=True)
        self.assertEqual(result['sent'][14], 1)
        self.assertEqual(len(mail.outbox), 0)

        doc.refresh_from_db()
        self.assertIsNone(doc.expiry_reminder_14_sent_at)

    def test_clear_expiry_reminder_fields(self):
        doc = self._verified_driver_license(expiry=date.today() + timedelta(days=30))
        doc.expiry_reminder_30_sent_at = timezone.now()
        doc.save(update_fields=['expiry_reminder_30_sent_at'])

        clear_expiry_reminder_fields(doc)
        doc.save(update_fields=[
            'expiry_reminder_30_sent_at',
            'expiry_reminder_14_sent_at',
            'expiry_reminder_0_sent_at',
        ])
        doc.refresh_from_db()
        self.assertIsNone(doc.expiry_reminder_30_sent_at)
