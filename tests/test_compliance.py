# Legal document compliance tests — Phase 4A

import os
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.compliance_constants import CoverageType, DocumentStatus, DocumentType
from delivery.compliance_service import (
    assert_vehicle_may_reactivate,
    create_document,
    get_compliance_summary,
    get_presigned_download_url,
    get_presigned_upload_url,
    get_vehicle_reactivation_blockers,
    is_vehicle_compliant,
    list_documents_for_driver,
    list_driver_owned_documents,
    mark_expired_documents,
    mark_rejected,
    mark_verified,
    update_document,
    user_can_access_vehicle,
)
from delivery import compliance_storage
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

    def test_list_documents_for_driver_includes_vehicle_docs(self):
        create_document(
            self.staff,
            vehicle=self.vehicle,
            data={'document_type': DocumentType.VEHICLE_REGISTRATION, 'issuer': 'DMV'},
        )
        docs = list_documents_for_driver(self.driver)
        self.assertEqual(docs.count(), 1)

    def test_list_driver_owned_documents_excludes_vehicle_docs(self):
        create_document(
            self.staff,
            driver=self.driver,
            data={'document_type': DocumentType.DRIVER_LICENSE, 'issuer': 'ICBC'},
        )
        create_document(
            self.staff,
            vehicle=self.vehicle,
            data={'document_type': DocumentType.VEHICLE_REGISTRATION, 'issuer': 'DMV'},
        )
        docs = list_driver_owned_documents(self.driver)
        self.assertEqual(docs.count(), 1)
        self.assertEqual(docs.first().document_type, DocumentType.DRIVER_LICENSE)

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
            data={
                'document_type': DocumentType.DRIVER_LICENSE,
                'expiry_date': date.today() + timedelta(days=365),
            },
        )
        mark_verified(self.staff, doc.id)
        doc.refresh_from_db()
        with self.assertRaises(PermissionDenied):
            update_document(self.driver_user, doc, {'issuer': 'Changed'})

    def test_create_document_rejects_foreign_file_key(self):
        with self.assertRaises(Exception):
            create_document(
                self.driver_user,
                driver=self.driver,
                data={
                    'document_type': DocumentType.DRIVER_LICENSE,
                    'file_key': 'compliance/staging/99999/abc/policy.pdf',
                    'file_name': 'policy.pdf',
                },
            )


class ComplianceStorageTests(TestCase):
    def test_sanitize_pdf_filename(self):
        self.assertEqual(
            compliance_storage.sanitize_pdf_filename('My Policy.PDF'),
            'My_Policy.pdf',
        )

    def test_reject_non_pdf_extension(self):
        with self.assertRaises(Exception):
            compliance_storage.sanitize_pdf_filename('policy.docx')

    def test_assert_file_key_owned_by_user(self):
        key = compliance_storage.build_staging_file_key(7, 'license.pdf')
        compliance_storage.assert_file_key_owned_by_user(7, key)
        with self.assertRaises(Exception):
            compliance_storage.assert_file_key_owned_by_user(8, key)


class CompliancePresignedUrlTests(TestCase):
    AWS_ENV = {
        'AWS_STORAGE_BUCKET_NAME': 'test-compliance-bucket',
        'AWS_ACCESS_KEY_ID': 'test-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret',
        'AWS_S3_REGION_NAME': 'us-east-1',
    }

    def setUp(self):
        self.user = User.objects.create_user(username='upload_user', password='pass')

    @patch.dict(os.environ, AWS_ENV, clear=False)
    @patch('delivery.compliance_storage._get_s3_client')
    def test_get_presigned_upload_url_pdf(self, mock_get_client):
        mock_get_client.return_value.generate_presigned_url.return_value = 'https://s3.example/upload'
        result = get_presigned_upload_url(
            self.user,
            file_name='commercial-policy.pdf',
            content_type='application/pdf',
            file_size=1024,
        )
        self.assertEqual(result['upload_url'], 'https://s3.example/upload')
        self.assertTrue(result['file_key'].startswith(f'compliance/staging/{self.user.id}/'))
        self.assertEqual(result['file_name'], 'commercial-policy.pdf')
        self.assertEqual(result['content_type'], 'application/pdf')

    @patch.dict(os.environ, AWS_ENV, clear=False)
    def test_get_presigned_upload_url_rejects_docx(self):
        with self.assertRaises(Exception):
            get_presigned_upload_url(
                self.user,
                file_name='policy.docx',
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            )

    @patch.dict(os.environ, AWS_ENV, clear=False)
    def test_get_presigned_upload_url_rejects_oversize(self):
        with self.assertRaises(Exception):
            get_presigned_upload_url(
                self.user,
                file_name='big.pdf',
                content_type='application/pdf',
                file_size=compliance_storage.MAX_COMPLIANCE_FILE_BYTES + 1,
            )

    @patch.dict(os.environ, AWS_ENV, clear=False)
    @patch('delivery.compliance_storage._get_s3_client')
    def test_get_presigned_download_url(self, mock_get_client):
        mock_get_client.return_value.generate_presigned_url.return_value = 'https://s3.example/download'
        staff = User.objects.create_user(username='staff_dl', password='pass', is_staff=True)
        driver_user = User.objects.create_user(username='driver_dl', password='pass')
        driver = Driver.objects.create(
            user=driver_user,
            phone_number='555-0300',
            license_number='DL-DL-001',
        )
        doc = create_document(
            driver_user,
            driver=driver,
            data={
                'document_type': DocumentType.DRIVER_LICENSE,
                'file_key': compliance_storage.build_staging_file_key(driver_user.id, 'license.pdf'),
                'file_name': 'license.pdf',
            },
        )
        result = get_presigned_download_url(staff, doc)
        self.assertEqual(result['download_url'], 'https://s3.example/download')
        self.assertEqual(result['file_name'], 'license.pdf')


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

    def test_driver_documents_list_excludes_vehicle_docs(self):
        self.driver_client.post(
            f'/api/drivers/{self.driver.id}/documents/',
            {'document_type': DocumentType.DRIVER_LICENSE, 'issuer': 'ICBC'},
            format='json',
        )
        self.driver_client.post(
            f'/api/vehicles/{self.vehicle.id}/documents/',
            {
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'issuer': 'Test Insurance Co.',
                'policy_number': 'POL-TEST-1',
                'coverage_type': CoverageType.COMMERCIAL,
                'expiry_date': str(date.today() + timedelta(days=365)),
            },
            format='json',
        )
        response = self.driver_client.get(f'/api/drivers/{self.driver.id}/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['document_type'], DocumentType.DRIVER_LICENSE)

        vehicle_response = self.driver_client.get(f'/api/vehicles/{self.vehicle.id}/documents/')
        self.assertEqual(len(vehicle_response.data), 1)
        self.assertEqual(
            vehicle_response.data[0]['document_type'],
            DocumentType.COMMERCIAL_INSURANCE,
        )

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
    def test_presigned_upload_missing_credentials(self):
        response = self.driver_client.post(
            '/api/documents/presigned-upload/',
            {'file_name': 'insurance.pdf', 'content_type': 'application/pdf'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('storage', response.data)

    @patch.dict(
        os.environ,
        {
            'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'AWS_S3_REGION_NAME': 'us-east-1',
        },
        clear=False,
    )
    @patch('delivery.compliance_storage._get_s3_client')
    def test_presigned_upload_pdf_success(self, mock_get_client):
        mock_get_client.return_value.generate_presigned_url.return_value = 'https://s3.example/upload'
        response = self.driver_client.post(
            '/api/documents/presigned-upload/',
            {
                'file_name': 'insurance.pdf',
                'content_type': 'application/pdf',
                'file_size': 2048,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['upload_url'], 'https://s3.example/upload')
        self.assertIn('file_key', response.data)

    def test_presigned_upload_rejects_docx(self):
        response = self.driver_client.post(
            '/api/documents/presigned-upload/',
            {
                'file_name': 'policy.docx',
                'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.dict(
        os.environ,
        {
            'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'AWS_S3_REGION_NAME': 'us-east-1',
        },
        clear=False,
    )
    @patch('delivery.compliance_storage._get_s3_client')
    def test_document_download_staff(self, mock_get_client):
        mock_get_client.return_value.generate_presigned_url.return_value = 'https://s3.example/download'
        file_key = compliance_storage.build_staging_file_key(self.driver_user.id, 'license.pdf')
        create_resp = self.driver_client.post(
            f'/api/drivers/{self.driver.id}/documents/',
            {
                'document_type': DocumentType.DRIVER_LICENSE,
                'file_key': file_key,
                'file_name': 'license.pdf',
            },
            format='json',
        )
        doc_id = create_resp.data['id']
        response = self.staff_client.get(f'/api/documents/{doc_id}/download/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['download_url'], 'https://s3.example/download')
        self.assertEqual(response.data['file_name'], 'license.pdf')

    @patch.dict(
        os.environ,
        {
            'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'AWS_S3_REGION_NAME': 'us-east-1',
        },
        clear=False,
    )
    @patch('delivery.compliance_storage._get_s3_client')
    def test_document_download_owner(self, mock_get_client):
        mock_get_client.return_value.generate_presigned_url.return_value = 'https://s3.example/download'
        file_key = compliance_storage.build_staging_file_key(self.driver_user.id, 'license.pdf')
        create_resp = self.driver_client.post(
            f'/api/drivers/{self.driver.id}/documents/',
            {
                'document_type': DocumentType.DRIVER_LICENSE,
                'file_key': file_key,
                'file_name': 'license.pdf',
            },
            format='json',
        )
        doc_id = create_resp.data['id']
        response = self.driver_client.get(f'/api/documents/{doc_id}/download/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_document_download_without_file(self):
        create_resp = self.driver_client.post(
            f'/api/drivers/{self.driver.id}/documents/',
            {'document_type': DocumentType.DRIVER_LICENSE},
            format='json',
        )
        doc_id = create_resp.data['id']
        response = self.driver_client.get(f'/api/documents/{doc_id}/download/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file_key', response.data)

    @patch.dict(
        os.environ,
        {
            'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'AWS_S3_REGION_NAME': 'us-east-1',
        },
        clear=False,
    )
    @patch('delivery.compliance_storage._get_s3_client')
    def test_document_upload_pdf(self, mock_get_client):
        mock_get_client.return_value.put_object.return_value = {}
        pdf_bytes = b'%PDF-1.4\n% test license\n'
        response = self.driver_client.post(
            '/api/documents/upload/',
            {'file': SimpleUploadedFile('license.pdf', pdf_bytes, content_type='application/pdf')},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file_key', response.data)
        self.assertEqual(response.data['file_name'], 'license.pdf')


def seed_verified_vehicle_compliance(staff, vehicle, *, days=60):
    """Helper: verified registration + commercial insurance for reactivation tests."""
    for doc_type in (DocumentType.VEHICLE_REGISTRATION, DocumentType.COMMERCIAL_INSURANCE):
        data = {
            'document_type': doc_type,
            'expiry_date': date.today() + timedelta(days=days),
        }
        if doc_type == DocumentType.COMMERCIAL_INSURANCE:
            data.update(
                coverage_type=CoverageType.COMMERCIAL,
                policy_number='POL-TEST',
                issuer='Acme Insurance',
            )
        doc = create_document(staff, vehicle=vehicle, data=data)
        mark_verified(staff, doc.id)


class Phase4BComplianceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff4b', password='pass', is_staff=True)
        self.vehicle = Vehicle.objects.create(
            license_plate='4B001',
            make='Ford',
            model='Transit',
            year=2022,
            vin='1FT4BTEST00000001',
            capacity=1500,
            capacity_unit='kg',
            active=False,
        )

    def test_mark_expired_documents_updates_verified_past_expiry(self):
        doc = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.VEHICLE_REGISTRATION,
                'expiry_date': date.today() - timedelta(days=1),
            },
        )
        mark_verified(self.staff, doc.id)
        count = mark_expired_documents(as_of_date=date.today())
        self.assertEqual(count, 1)
        doc.refresh_from_db()
        self.assertEqual(doc.status, DocumentStatus.EXPIRED)

    def test_reactivation_blockers_when_docs_missing(self):
        blockers = get_vehicle_reactivation_blockers(self.vehicle)
        self.assertIn('vehicle_registration_missing', blockers)
        self.assertIn('commercial_insurance_missing', blockers)

    def test_reactivation_blockers_when_docs_expired(self):
        reg = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.VEHICLE_REGISTRATION,
                'expiry_date': date.today() - timedelta(days=5),
            },
        )
        mark_verified(self.staff, reg.id)
        mark_expired_documents()
        ins = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'coverage_type': CoverageType.COMMERCIAL,
                'policy_number': 'P1',
                'issuer': 'Acme',
                'expiry_date': date.today() - timedelta(days=2),
            },
        )
        mark_verified(self.staff, ins.id)
        mark_expired_documents()
        blockers = get_vehicle_reactivation_blockers(self.vehicle)
        self.assertIn('vehicle_registration_expired', blockers)
        self.assertIn('commercial_insurance_expired', blockers)

    def test_assert_vehicle_may_reactivate_raises_compliance_error(self):
        with self.assertRaises(Exception) as ctx:
            assert_vehicle_may_reactivate(self.vehicle)
        self.assertIn('compliance', getattr(ctx.exception, 'detail', ctx.exception.args[0]))

    def test_is_vehicle_compliant_when_docs_current(self):
        seed_verified_vehicle_compliance(self.staff, self.vehicle)
        status = is_vehicle_compliant(self.vehicle)
        self.assertTrue(status['compliant'])
        self.assertTrue(status['may_reactivate'])
        self.assertEqual(status['blockers'], [])

    def test_mark_verified_requires_expiry_for_registration(self):
        doc = create_document(
            self.staff,
            vehicle=self.vehicle,
            data={'document_type': DocumentType.VEHICLE_REGISTRATION},
        )
        with self.assertRaises(Exception):
            mark_verified(self.staff, doc.id)


class Phase4BComplianceAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff4bapi', password='pass', is_staff=True)
        self.staff_client = auth_client(self.staff)
        self.vehicle = Vehicle.objects.create(
            license_plate='4BAPI1',
            make='Ford',
            model='Transit',
            year=2022,
            vin='1FT4BAPITEST0001',
            capacity=1500,
            capacity_unit='kg',
            active=False,
        )

    def test_vehicle_compliance_status_endpoint(self):
        seed_verified_vehicle_compliance(self.staff, self.vehicle)
        response = self.staff_client.get(f'/api/vehicles/{self.vehicle.id}/compliance-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['compliant'])
        self.assertTrue(response.data['may_reactivate'])

    def test_reactivate_blocked_without_compliance(self):
        response = self.staff_client.post(f'/api/vehicles/{self.vehicle.id}/reactivate/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('compliance', response.data)

    def test_reactivate_succeeds_with_compliance(self):
        seed_verified_vehicle_compliance(self.staff, self.vehicle)
        response = self.staff_client.post(f'/api/vehicles/{self.vehicle.id}/reactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertTrue(self.vehicle.active)
