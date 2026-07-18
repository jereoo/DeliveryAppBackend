# Driver registration approval workflow

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import Driver, DriverApprovalStatus, DriverVehicle, Vehicle


def auth_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


class DriverApprovalTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff_approval', password='pass', is_staff=True)
        self.staff_client = auth_client(self.staff)
        self.driver_user = User.objects.create_user(username='pending_driver', password='pass')
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='5557778888',
            license_number='DL-PEND-001',
            first_name='Pending',
            last_name='Driver',
            active=False,
            approval_status=DriverApprovalStatus.PENDING,
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='PEND001',
            make='Ford',
            model='F-150',
            year=2022,
            vin='1PENDTEST00000001',
            capacity=1500,
            capacity_unit='kg',
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    def test_staff_approves_pending_driver(self):
        response = self.staff_client.post(f'/api/drivers/{self.driver.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.approval_status, DriverApprovalStatus.APPROVED)
        self.assertTrue(self.driver.active)
        self.assertIsNotNone(self.driver.approved_at)

    def test_staff_rejects_pending_driver(self):
        response = self.staff_client.post(
            f'/api/drivers/{self.driver.id}/reject/',
            {'rejection_reason': 'Incomplete information'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.approval_status, DriverApprovalStatus.REJECTED)
        self.assertFalse(self.driver.active)
        self.assertEqual(self.driver.approval_rejection_reason, 'Incomplete information')

    def test_dispatch_blocked_for_pending_driver(self):
        from delivery.compliance_service import is_driver_eligible_for_dispatch

        result = is_driver_eligible_for_dispatch(self.driver)
        self.assertFalse(result['eligible'])
        self.assertIn('driver_pending_approval', result['blockers'])
