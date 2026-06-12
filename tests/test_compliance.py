# Legal document compliance tests — Phase 4A

import os
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.compliance_constants import CoverageType, DocumentStatus, DocumentType
from delivery.compliance_service import (
    create_document,
    get_compliance_summary,
    list_documents_for_driver,
    mark_rejected,
    mark_verified,
    update_document,
    user_can_access_vehicle,
)
from delivery.models import Driver, DriverVehicle, LegalDocument, Vehicle


def auth_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


class LegalDocumentModelTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='driver1', password='pass')
        self.driver = Driver.objects.create(
            user=user,
            phone_number='555-0100',
            license_number='DL-TEST-001',
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='TEST001',
            make='Ford',
            model='Transit',
            year=2022,
            vin='1FTBR1XM5NKA12345',
            capacity=1500,
            capacity_unit='kg',
        )

    def test_driver_license_requires_driver_not_vehicle(self):
        doc = LegalDocument(
            document_type=DocumentType.DRIVER_LICENSE,
            driver=self.driver,
            status=DocumentStatus.PENDING,
        )
        doc.full_clean()
        doc.save()

        bad = LegalDocument(
            document_type=DocumentType.DRIVER_LICENSE,
            vehicle=self.vehicle,
            status=DocumentStatus.PENDING,
        )
        with self.assertRaises(ValidationError):
            bad.full_clean()

    def test_vehicle_insurance_requires_vehicle_not_driver(self):
        doc = LegalDocument(
            document_type=DocumentType.COMMERCIAL_INSURANCE,
            vehicle=self.vehicle,
            coverage_type=CoverageType.COMMERCIAL,
            policy_number='POL-123',
            issuer='Acme Insurance',
            status=DocumentStatus.PENDING,
        )
        doc.full_clean()
        doc.save()

        bad = LegalDocument(
            document_type=DocumentType.COMMERCIAL_INSURANCE,
            driver=self.driver,
            status=DocumentStatus.PENDING,
        )
        with self.assertRaises(ValidationError):
            bad.full_clean()

    def test_expiry_before_effective_rejected(self):
        doc = LegalDocument(
            document_type=DocumentType.VEHICLE_REGISTRATION,
            vehicle=self.vehicle,
            effective_date=date(2026, 6, 1),
            expiry_date=date(2026, 1, 1),
            status=DocumentStatus.PENDING,
        )
        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_str_includes_type_and_status(self):
        doc = LegalDocument.objects.create(
            document_type=DocumentType.DRIVER_LICENSE,
            driver=self.driver,
            status=DocumentStatus.PENDING,
        )
        self.assertIn('Driver license', str(doc))
        self.assertIn('PENDING', str(doc))


class ComplianceServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.driver_user = User.objects.create_user(username='driver', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='555-0100',
            license_number='DL-SVC-001',
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='SVC001',
            make='Ford',
            model='Transit',
            year=2022,
            vin='1FTBR1XM5NKA54321',
            capacity=1500,
            capacity_unit='kg',
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    def test_create_driver_license_for_own_driver(self):
        doc = create_document(
            self.driver_user,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE, 'issuer': 'DMV'},
        )
        self.assertEqual(doc.status, DocumentStatus.PENDING)
        self.assertEqual(doc.driver_id, self.driver.id)

    def test_driver_cannot_create_for_other_driver(self):
        other = Driver.objects.create(
            user=self.other_user,
            phone_number='555-0200',
            license_number='DL-OTHER-001',
        )
        with self.assertRaises(NotFound):
            create_document(
                self.driver_user,
                driver=other,
                data={'document_type': DocumentType.DRIVER_LICENSE},
            )

    def test_mark_verified_requires_commercial_coverage(self):
        doc = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'issuer': 'Acme',
                'policy_number': 'P1',
                'coverage_type': CoverageType.PERSONAL,
                'expiry_date': date.today() + timedelta(days=30),
            },
        )
        with self.assertRaises(Exception):
            mark_verified(self.staff, doc.id)

    def test_mark_verified_commercial_insurance(self):
        doc = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'issuer': 'Acme',
                'policy_number': 'P1',
                'coverage_type': CoverageType.COMMERCIAL,
                'expiry_date': date.today() + timedelta(days=30),
            },
        )
        verified = mark_verified(self.staff, doc.id, notes='Looks good')
        self.assertEqual(verified.status, DocumentStatus.VERIFIED)
        self.assertEqual(verified.verified_by_id, self.staff.id)

    def test_driver_cannot_verify(self):
        doc = create_document(
            self.driver_user,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE},
        )
        with self.assertRaises(PermissionDenied):
            mark_verified(self.driver_user, doc.id)

    def test_mark_rejected_requires_reason(self):
        doc = create_document(
            self.staff,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE},
        )
        with self.assertRaises(Exception):
            mark_rejected(self.staff, doc.id, reason='')

    def test_compliance_summary_missing_types(self):
        summary = get_compliance_summary(self.driver)
        self.assertIn(DocumentType.DRIVER_LICENSE, summary['missing_types'])
        self.assertIn(DocumentType.COMMERCIAL_INSURANCE, summary['missing_types'])
        self.assertFalse(summary['is_fully_compliant'])

    def test_list_documents_includes_vehicle_docs(self):
        create_document(
            self.staff,
            vehicle=self.vehicle,
            data={'document_type': DocumentType.VEHICLE_REGISTRATION, 'issuer': 'DMV'},
        )
        docs = list_documents_for_driver(self.driver)
        self.assertEqual(docs.count(), 1)

    def test_driver_can_update_pending_document(self):
        doc = create_document(
            self.driver_user,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE, 'issuer': 'Old'},
        )
        updated = update_document(self.driver_user, doc, {'issuer': 'New DMV'})
        self.assertEqual(updated.issuer, 'New DMV')

    def test_driver_cannot_update_verified_document(self):
        doc = create_document(
            self.staff,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE},
        )
        mark_verified(self.staff, doc.id)
        doc.refresh_from_db()
        with self.assertRaises(PermissionDenied):
            update_document(self.driver_user, doc, {'issuer': 'Changed'})


class ComplianceAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff_api', password='pass', is_staff=True)
        self.staff_client = auth_client(self.staff)
        self.driver_user = User.objects.create_user(username='driver_api', password='pass')
        self.driver_client = auth_client(self.driver_user)
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='555-0100',
            license_number='DL-API-001',
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='API001',
            make='Ford',
            model='Transit',
            year=2022,
            vin='1FTBR1XM5NKA99999',
            capacity=1500,
            capacity_unit='kg',
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    def test_driver_lists_own_documents(self):
        response = self.driver_client.post(
            f'/api/drivers/{self.driver.id}/documents/',
            {'document_type': DocumentType.DRIVER_LICENSE, 'issuer': 'DMV'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.driver_client.get(f'/api/drivers/{self.driver.id}/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_driver_posts_vehicle_document(self):
        response = self.driver_client.post(
            f'/api/vehicles/{self.vehicle.id}/documents/',
            {
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'issuer': 'Acme',
                'policy_number': 'POL-99',
                'coverage_type': CoverageType.COMMERCIAL,
                'expiry_date': str(date.today() + timedelta(days=60)),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_verifies_insurance(self):
        create_resp = self.driver_client.post(
            f'/api/vehicles/{self.vehicle.id}/documents/',
            {
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'issuer': 'Acme',
                'policy_number': 'POL-99',
                'coverage_type': CoverageType.COMMERCIAL,
                'expiry_date': str(date.today() + timedelta(days=60)),
            },
            format='json',
        )
        doc_id = create_resp.data['id']
        response = self.staff_client.post(f'/api/documents/{doc_id}/verify/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], DocumentStatus.VERIFIED)

    def test_staff_rejects_document(self):
        create_resp = self.driver_client.post(
            f'/api/drivers/{self.driver.id}/documents/',
            {'document_type': DocumentType.DRIVER_LICENSE},
            format='json',
        )
        doc_id = create_resp.data['id']
        response = self.staff_client.post(
            f'/api/documents/{doc_id}/reject/',
            {'rejection_reason': 'Illegible scan'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], DocumentStatus.REJECTED)

    def test_driver_compliance_status(self):
        response = self.driver_client.get('/api/drivers/me/compliance-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('missing_types', response.data)
        self.assertFalse(response.data['is_fully_compliant'])

    def test_driver_cannot_access_unassigned_vehicle_documents(self):
        other_vehicle = Vehicle.objects.create(
            license_plate='OTHER001',
            make='Toyota',
            model='Hiace',
            year=2021,
            vin='1OTHER12345678901',
            capacity=1200,
            capacity_unit='kg',
        )
        self.assertFalse(user_can_access_vehicle(self.driver_user, other_vehicle))
        response = self.driver_client.get(f'/api/vehicles/{other_vehicle.id}/documents/')
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_presigned_upload_without_s3_config(self):
        response = self.driver_client.post(
            '/api/documents/presigned-upload/',
            {'file_name': 'insurance.pdf', 'content_type': 'application/pdf'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.dict(os.environ, {'AWS_STORAGE_BUCKET_NAME': 'test-bucket'}, clear=False)
    def test_presigned_upload_not_implemented_yet(self):
        response = self.driver_client.post(
            '/api/documents/presigned-upload/',
            {'file_name': 'insurance.pdf', 'content_type': 'application/pdf'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('storage', response.data)
