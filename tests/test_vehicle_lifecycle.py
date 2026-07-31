"""Vehicle approval, replace, and immutability tests."""

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import Driver, DriverVehicle, Vehicle, VehicleApprovalStatus
from tests.vehicle_catalog_helpers import get_catalog_spec_id


def auth_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


class VehicleLifecycleTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff_vlc',
            password='testpass123',
            is_staff=True,
        )
        self.staff_client = auth_client(self.staff)
        self.driver_user = User.objects.create_user(
            username='driver_vlc',
            password='testpass123',
            first_name='Val',
            last_name='Driver',
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            first_name='Val',
            last_name='Driver',
            phone_number='6045550199',
            license_number='DL-VLC-1',
            active=True,
        )
        self.driver_client = auth_client(self.driver_user)
        self.spec_id = get_catalog_spec_id('Ford', 'F-150')
        self.vehicle = Vehicle.objects.create(
            license_plate='VLC001',
            make='Ford',
            model='F-150',
            year=2020,
            vin='1VLCTESTVIN000001',
            capacity=3325,
            capacity_unit='lb',
            active=True,
            approval_status=VehicleApprovalStatus.APPROVED,
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date(),
        )

    def test_driver_cannot_patch_identity_on_approved_vehicle(self):
        response = self.driver_client.patch('/api/drivers/me/vehicle/', {
            'year': 2021,
            'make': 'Chevy',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_resubmit_sets_inactive_and_reason(self):
        response = self.staff_client.post(f'/api/vehicles/{self.vehicle.id}/resubmit/', {
            'resubmit_reason': 'Correct the vehicle year to 2019.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.approval_status, VehicleApprovalStatus.RESUBMIT)
        self.assertFalse(self.vehicle.active)
        self.assertIn('year', self.vehicle.resubmit_reason)

    def test_staff_cannot_edit_approved_vehicle_identity_via_patch(self):
        response = self.staff_client.patch(f'/api/vehicles/{self.vehicle.id}/', {
            'year': 2018,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_replace_vehicle_creates_pending_inactive_vehicle(self):
        response = self.driver_client.post('/api/drivers/me/vehicles/', {
            'vehicle_model_spec_id': self.spec_id,
            'vehicle_year': 2021,
            'vehicle_license_plate': 'VLC002',
            'vehicle_vin': '1VLCTESTVIN000002',
            'vehicle_capacity': 3325,
            'vehicle_capacity_unit': 'lb',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_id = response.data['vehicle']['id']
        new_vehicle = Vehicle.objects.get(pk=new_id)
        self.assertEqual(new_vehicle.approval_status, VehicleApprovalStatus.PENDING)
        self.assertFalse(new_vehicle.active)
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.active)

    def test_dispatch_blocked_for_pending_vehicle(self):
        pending = Vehicle.objects.create(
            license_plate='VLC003',
            make='Ford',
            model='F-150',
            year=2021,
            vin='1VLCTESTVIN000003',
            capacity=3325,
            capacity_unit='lb',
            active=False,
            approval_status=VehicleApprovalStatus.PENDING,
        )
        DriverVehicle.objects.filter(driver=self.driver, assigned_to__isnull=True).update(
            assigned_to=timezone.now().date(),
        )
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=pending,
            assigned_from=timezone.now().date(),
        )
        response = self.driver_client.get(f'/api/drivers/{self.driver.id}/dispatch-eligibility/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('vehicle_pending_approval', response.data['blockers'])
