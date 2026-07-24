# Phase 4D — admin compliance ops API

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.compliance_constants import DocumentStatus, DocumentType
from delivery.compliance_service import create_document, mark_verified
from delivery.models import Driver, DriverApprovalStatus, DriverVehicle, Vehicle


def auth_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


class ComplianceAdminAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff4d', password='pass', is_staff=True)
        self.staff_client = auth_client(self.staff)
        self.driver_user = User.objects.create_user(username='driver4d', password='pass')
        self.driver = Driver.objects.create(
            user=self.driver_user,
            first_name='Pat',
            last_name='Driver',
            phone_number='555-0400',
            license_number='DL-4D-001',
            license_issuing_region='CA-BC',
            approval_status=DriverApprovalStatus.PENDING,
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='4D001',
            make='Ford',
            model='F-150',
            year=2022,
            vin='1FT4DTEST0000001',
            capacity=1200,
            capacity_unit='kg',
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    def test_summary_requires_staff(self):
        client = auth_client(self.driver_user)
        response = client.get('/api/compliance/admin/summary/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_summary_returns_fleet_counts(self):
        pending_doc = create_document(
            self.staff,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE},
        )
        self.assertEqual(pending_doc.status, DocumentStatus.PENDING)

        response = self.staff_client.get('/api/compliance/admin/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['documents_pending'], 1)
        self.assertGreaterEqual(response.data['drivers_pending_approval'], 1)

    def test_inbox_lists_pending_documents(self):
        create_document(
            self.staff,
            vehicle=self.vehicle,
            data={'document_type': DocumentType.VEHICLE_REGISTRATION},
        )
        response = self.staff_client.get('/api/compliance/admin/inbox/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        row = response.data[0]
        self.assertIn('document_id', row)
        self.assertIn('driver_name', row)
        self.assertEqual(row['status'], DocumentStatus.PENDING)

    def test_expiring_lists_soon_and_expired_docs(self):
        expiring = create_document(
            self.staff,
            driver=self.driver,
            data={
                'document_type': DocumentType.DRIVER_LICENSE,
                'expiry_date': date.today() + timedelta(days=10),
            },
        )
        mark_verified(self.staff, expiring.id)

        expired = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.VEHICLE_REGISTRATION,
                'expiry_date': date.today() - timedelta(days=3),
            },
        )
        mark_verified(self.staff, expired.id)
        expired.status = DocumentStatus.EXPIRED
        expired.save(update_fields=['status'])

        response = self.staff_client.get('/api/compliance/admin/expiring/?days=30')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc_types = {row['document_type'] for row in response.data}
        self.assertIn(DocumentType.DRIVER_LICENSE, doc_types)
        self.assertIn(DocumentType.VEHICLE_REGISTRATION, doc_types)
