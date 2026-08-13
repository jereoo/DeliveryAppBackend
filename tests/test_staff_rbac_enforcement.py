"""Phase 4G Slice 3 — role permission enforcement on operational endpoints."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import (
    Customer,
    Delivery,
    Driver,
    DriverApprovalStatus,
    DriverVehicle,
    LegalDocument,
    StaffProfile,
    Vehicle,
)
from delivery.compliance_constants import DocumentStatus, DocumentType
from delivery.staff_constants import StaffRole


class StaffRbacEnforcementTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_admin = self._make_staff('superadmin', StaffRole.SUPER_ADMIN)
        self.ops_admin = self._make_staff('opsadmin', StaffRole.OPERATIONS_ADMIN)
        self.reviewer = self._make_staff('reviewer', StaffRole.COMPLIANCE_REVIEWER)
        self.read_only = self._make_staff('readonly', StaffRole.READ_ONLY)

        self.customer_user = User.objects.create_user(
            username='cust1',
            email='cust1@example.com',
            password='testpass123',
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone_number='5552001',
            address_country='US',
        )
        self.pending_driver_user = User.objects.create_user(
            username='pendingdriver',
            email='pending@example.com',
            password='testpass123',
        )
        self.pending_driver = Driver.objects.create(
            user=self.pending_driver_user,
            phone_number='5552002',
            license_number='RBACDL001',
            approval_status=DriverApprovalStatus.PENDING,
            active=False,
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='RBAC01',
            make='Ford',
            model='F-150',
            year=2022,
            vin='1RBACTESTVIN000001',
            capacity=1500,
            capacity_unit='kg',
            active=False,
        )
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='123 Pickup St',
            dropoff_location='456 Dropoff Ave',
            status='Pending',
        )
        self.pending_doc = LegalDocument.objects.create(
            driver=self.pending_driver,
            document_type=DocumentType.DRIVER_LICENSE,
            status=DocumentStatus.PENDING,
            file_name='license.pdf',
        )

    def _make_staff(self, username: str, role: str) -> User:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=(role == StaffRole.SUPER_ADMIN),
        )
        StaffProfile.objects.create(user=user, staff_role=role)
        return user

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_read_only_cannot_create_customer(self):
        self._auth(self.read_only)
        response = self.client.post('/api/customers/', {
            'username': 'newcust',
            'email': 'newcust@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Customer',
            'phone_number': '5553003000',
            'address_country': 'US',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_only_can_list_drivers(self):
        self._auth(self.read_only)
        response = self.client.get('/api/drivers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_compliance_reviewer_cannot_approve_driver(self):
        self._auth(self.reviewer)
        response = self.client.post(f'/api/drivers/{self.pending_driver.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_operations_admin_can_approve_driver(self):
        self._auth(self.ops_admin)
        response = self.client.post(f'/api/drivers/{self.pending_driver.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_compliance_reviewer_can_verify_document(self):
        self._auth(self.reviewer)
        response = self.client.post(
            f'/api/documents/{self.pending_doc.id}/verify/',
            {'expiry_date': '2030-12-31'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_only_cannot_verify_document(self):
        doc = LegalDocument.objects.create(
            driver=self.pending_driver,
            document_type=DocumentType.DRIVER_LICENSE,
            status=DocumentStatus.PENDING,
            file_name='license2.pdf',
        )
        self._auth(self.read_only)
        response = self.client.post(
            f'/api/documents/{doc.id}/verify/',
            {'expiry_date': '2030-12-31'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_compliance_reviewer_cannot_create_delivery_assignment(self):
        self._auth(self.reviewer)
        response = self.client.post('/api/assignments/', {
            'delivery': self.delivery.id,
            'driver': self.pending_driver.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_operations_admin_can_create_delivery_assignment(self):
        eligible_driver = Driver.objects.create(
            user=User.objects.create_user(
                username='eligibledriver',
                email='eligible@example.com',
                password='testpass123',
            ),
            phone_number='5552003',
            license_number='RBACDL002',
            approval_status=DriverApprovalStatus.APPROVED,
            active=True,
        )
        DriverVehicle.objects.create(
            driver=eligible_driver,
            vehicle=self.vehicle,
            assigned_from='2026-01-01',
        )
        self._auth(self.ops_admin)
        response = self.client.post('/api/assignments/', {
            'delivery': self.delivery.id,
            'driver': eligible_driver.id,
        }, format='json')
        self.assertIn(response.status_code, (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST))

    def test_read_only_cannot_reactivate_vehicle(self):
        self._auth(self.read_only)
        response = self.client.post(f'/api/vehicles/{self.vehicle.id}/reactivate/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_operations_admin_can_reactivate_vehicle(self):
        self._auth(self.ops_admin)
        response = self.client.post(f'/api/vehicles/{self.vehicle.id}/reactivate/')
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
