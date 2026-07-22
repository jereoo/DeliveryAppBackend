# Driver/vehicle/legal-document seed tests

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from delivery.compliance_constants import DocumentStatus, DocumentType
from delivery.models import Driver, DriverVehicle, LegalDocument, Vehicle
from delivery.models import DriverApprovalStatus
from delivery.seed_driver_vehicle_test_data import (
    TEST_DRIVER_PASSWORD,
    clear_driver_vehicle_data,
    get_test_driver_usernames,
    seed_driver_vehicle_test_data,
)


class SeedDriverVehicleTestDataTests(TestCase):
    def test_clear_removes_drivers_vehicles_and_docs(self):
        user = User.objects.create_user(username='old.driver', password='x')
        driver = Driver.objects.create(
            user=user,
            phone_number='555',
            license_number='OLD-001',
            license_issuing_region='CA-BC',
        )
        vehicle = Vehicle.objects.create(
            license_plate='OLDPLATE',
            make='Ford',
            model='F-150',
            year=2020,
            vin='1OLDVIN000000001',
            capacity=1000,
        )
        DriverVehicle.objects.create(driver=driver, vehicle=vehicle, assigned_from='2026-01-01')
        doc = LegalDocument(
            document_type=DocumentType.DRIVER_LICENSE,
            driver=driver,
            status=DocumentStatus.PENDING,
        )
        doc.save(validate=False)

        counts = clear_driver_vehicle_data()
        self.assertEqual(counts['drivers'], 1)
        self.assertFalse(Driver.objects.exists())
        self.assertFalse(Vehicle.objects.exists())
        self.assertFalse(LegalDocument.objects.exists())
        self.assertFalse(User.objects.filter(username='old.driver').exists())

    def test_seed_creates_catalog_compliant_profiles(self):
        result = seed_driver_vehicle_test_data(force=True)
        self.assertFalse(result['skipped'])
        self.assertEqual(len(result['profiles']), len(get_test_driver_usernames()))

        approved = Driver.objects.get(user__username='test.driver.approved')
        self.assertEqual(approved.license_issuing_region, 'CA-BC')
        self.assertEqual(approved.approval_status, DriverApprovalStatus.APPROVED)
        self.assertTrue(approved.active)
        self.assertIsNotNone(approved.user.check_password(TEST_DRIVER_PASSWORD))

        vehicle = Vehicle.objects.get(license_plate='TEST001')
        self.assertIsNotNone(vehicle.model_spec_id)
        self.assertEqual(vehicle.make, 'Ford')
        self.assertEqual(vehicle.model, 'F-150')

        verified_docs = LegalDocument.objects.filter(
            driver=approved,
            status=DocumentStatus.VERIFIED,
        ).count()
        self.assertEqual(verified_docs, 1)

        vehicle_docs = LegalDocument.objects.filter(
            vehicle=vehicle,
            status=DocumentStatus.VERIFIED,
        ).count()
        self.assertEqual(vehicle_docs, 2)

    def test_seed_skips_when_other_drivers_exist_without_force(self):
        user = User.objects.create_user(username='legacy.driver', password='x')
        Driver.objects.create(
            user=user,
            phone_number='555',
            license_number='LEG-001',
        )
        result = seed_driver_vehicle_test_data(force=False)
        self.assertTrue(result['skipped'])

    def test_management_command_force(self):
        call_command('seed_driver_vehicle_test_data', '--force')
        self.assertTrue(Driver.objects.filter(user__username='test.driver.pending').exists())
        pending = Driver.objects.get(user__username='test.driver.pending')
        self.assertEqual(pending.approval_status, DriverApprovalStatus.PENDING)
        pending_docs = LegalDocument.objects.filter(
            status=DocumentStatus.PENDING,
        ).count()
        self.assertGreaterEqual(pending_docs, 3)
