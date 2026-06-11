"""
Driver profile and driver-owned vehicle CRUD tests.

Covers:
- Staff admin driver CRUD + vehicle assignment
- Driver self-service /drivers/me/ and /drivers/me/vehicle/
- Vehicle lifecycle (inactive / reactivate) from driver and staff perspectives
- Driver registration with vehicle
"""
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import Driver, DriverVehicle, Vehicle
from delivery.vehicle_constants import MAX_VEHICLE_CAPACITY_KG, MAX_VEHICLE_CAPACITY_LB, max_vehicle_capacity_for_unit


def auth_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


class DriverVehicleCRUDFixtures:
    """Shared fixtures for driver + vehicle CRUD tests."""

    @classmethod
    def create_staff(cls):
        return User.objects.create_user(
            username='staff_crud',
            password='testpass123',
            is_staff=True,
        )

    @classmethod
    def create_driver_user(cls, suffix='1'):
        user = User.objects.create_user(
            username=f'driver_crud_{suffix}',
            email=f'driver_crud_{suffix}@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Driver',
        )
        driver = Driver.objects.create(
            user=user,
            first_name='Jane',
            last_name='Driver',
            phone_number='5551234567',
            license_number=f'DL-CRUD-{suffix}',
            active=True,
        )
        return user, driver

    @classmethod
    def create_vehicle(cls, suffix='1', active=True):
        safe = ''.join(c for c in str(suffix) if c.isalnum())[:8] or '1'
        return Vehicle.objects.create(
            license_plate=f'CRUD{safe}'[:20],
            make='Ford',
            model='Transit',
            year=2022,
            vin=f'1CRUD{safe:0>11}'[:17],
            capacity=1500,
            capacity_unit='kg',
            active=active,
        )

    @classmethod
    def assign_vehicle(cls, driver, vehicle, assigned_from=None):
        return DriverVehicle.objects.create(
            driver=driver,
            vehicle=vehicle,
            assigned_from=assigned_from or timezone.now().date(),
        )


class AdminDriverCRUDTests(APITestCase, DriverVehicleCRUDFixtures):
    """Staff CRUD on drivers and vehicle assignment."""

    def setUp(self):
        self.staff = self.create_staff()
        self.staff_client = auth_client(self.staff)
        self.driver_user, self.driver = self.create_driver_user('admin')
        self.vehicle = self.create_vehicle('v1')
        self.assign_vehicle(self.driver, self.vehicle)

    def test_staff_lists_all_drivers(self):
        response = self.staff_client.get('/api/drivers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [d['id'] for d in response.data['results']]
        self.assertIn(self.driver.id, ids)

    def test_staff_gets_driver_detail(self):
        response = self.staff_client.get(f'/api/drivers/{self.driver.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_number'], self.driver.license_number)
        self.assertEqual(response.data['current_vehicle_plate'], self.vehicle.license_plate)

    def test_staff_create_driver_via_standard_endpoint_requires_user_link(self):
        """POST /drivers/ has read-only user; staff create driver+account uses /register/."""
        new_user = User.objects.create_user(
            username='newadmin_driver',
            password='testpass123',
            first_name='New',
            last_name='Driver',
        )
        response = self.staff_client.post('/api/drivers/', {
            'user': new_user.id,
            'first_name': 'New',
            'last_name': 'Driver',
            'phone_number': '5559998888',
            'license_number': 'DL-NEW-001',
            'active': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_creates_vehicle(self):
        response = self.staff_client.post('/api/vehicles/', {
            'license_plate': 'STAFFNEW1',
            'make': 'Ram',
            'model': 'ProMaster',
            'year': 2023,
            'vin': '1STAFFCREATE00001',
            'capacity': 1800,
            'capacity_unit': 'kg',
            'active': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vehicle.objects.filter(license_plate='STAFFNEW1').exists())

    def test_staff_updates_vehicle(self):
        response = self.staff_client.patch(f'/api/vehicles/{self.vehicle.id}/', {
            'model': 'Transit Custom',
            'capacity': 1600,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.model, 'Transit Custom')
        self.assertEqual(self.vehicle.capacity, 1600)

    def test_staff_updates_driver(self):
        response = self.staff_client.patch(f'/api/drivers/{self.driver.id}/', {
            'phone_number': '5551112222',
            'first_name': 'Janet',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.phone_number, '5551112222')
        self.assertEqual(self.driver.first_name, 'Janet')

    def test_staff_deletes_driver(self):
        orphan_user = User.objects.create_user(username='orphan_drv', password='testpass123')
        orphan = Driver.objects.create(
            user=orphan_user,
            first_name='Orphan',
            last_name='Driver',
            phone_number='5550000001',
            license_number='DL-ORPHAN',
        )
        response = self.staff_client.delete(f'/api/drivers/{orphan.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Driver.objects.filter(pk=orphan.id).exists())

    def test_non_staff_cannot_create_driver_via_admin_endpoint(self):
        client = auth_client(self.driver_user)
        new_user = User.objects.create_user(username='blocked_drv', password='testpass123')
        response = client.post('/api/drivers/', {
            'user': new_user.id,
            'first_name': 'Blocked',
            'last_name': 'Driver',
            'phone_number': '5550000002',
            'license_number': 'DL-BLOCK',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_assigns_vehicle_to_driver(self):
        other_vehicle = self.create_vehicle('v2')
        response = self.staff_client.post(
            f'/api/drivers/{self.driver.id}/assign_vehicle/',
            {'vehicle_id': other_vehicle.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assignment']['vehicle'], other_vehicle.id)

    def test_staff_patches_vehicle_active_via_update(self):
        self.vehicle.active = False
        self.vehicle.save(update_fields=['active'])
        response = self.staff_client.patch(f'/api/vehicles/{self.vehicle.id}/', {
            'active': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertTrue(self.vehicle.active)


class DriverProfileCRUDTests(APITestCase, DriverVehicleCRUDFixtures):
    """Driver self-service profile CRUD via /drivers/me/."""

    def setUp(self):
        self.driver_user, self.driver = self.create_driver_user('me')
        self.client = auth_client(self.driver_user)
        self.other_user, self.other_driver = self.create_driver_user('other')

    def test_driver_me_get(self):
        response = self.client.get('/api/drivers/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_number'], self.driver.license_number)
        self.assertEqual(response.data['first_name'], 'Jane')

    def test_driver_me_patch_updates_profile(self):
        response = self.client.patch('/api/drivers/me/', {
            'phone_number': '5557778888',
            'last_name': 'Updated',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.phone_number, '5557778888')
        self.assertEqual(self.driver.last_name, 'Updated')
        self.driver_user.refresh_from_db()
        self.assertEqual(self.driver_user.last_name, 'Updated')

    def test_driver_me_cannot_toggle_active_flag(self):
        response = self.client.patch('/api/drivers/me/', {'active': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver.refresh_from_db()
        self.assertTrue(self.driver.active)

    def test_driver_sees_only_own_row_in_list(self):
        response = self.client.get('/api/drivers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.driver.id)

    def test_driver_cannot_read_other_driver_detail(self):
        response = self.client.get(f'/api/drivers/{self.other_driver.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_driver_cannot_delete_driver_record(self):
        response = self.client.delete(f'/api/drivers/{self.driver.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DriverOwnedVehicleCRUDTests(APITestCase, DriverVehicleCRUDFixtures):
    """Driver self-service vehicle CRUD via /drivers/me/vehicle/."""

    def setUp(self):
        self.staff = self.create_staff()
        self.staff_client = auth_client(self.staff)
        self.driver_user, self.driver = self.create_driver_user('veh')
        self.vehicle = self.create_vehicle('veh')
        self.assignment = self.assign_vehicle(self.driver, self.vehicle)
        self.client = auth_client(self.driver_user)

    def test_driver_me_vehicle_get_includes_active(self):
        response = self.client.get('/api/drivers/me/vehicle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_plate'], self.vehicle.license_plate)
        self.assertIn('active', response.data)
        self.assertTrue(response.data['active'])

    def test_driver_me_vehicle_patch_rejects_capacity_over_kg_limit(self):
        response = self.client.patch('/api/drivers/me/vehicle/', {
            'capacity': MAX_VEHICLE_CAPACITY_KG + 1,
            'capacity_unit': 'kg',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('capacity', response.data)

    def test_driver_me_vehicle_patch_allows_capacity_at_lb_limit(self):
        response = self.client.patch('/api/drivers/me/vehicle/', {
            'capacity': MAX_VEHICLE_CAPACITY_LB,
            'capacity_unit': 'lb',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.capacity, MAX_VEHICLE_CAPACITY_LB)
        self.assertEqual(self.vehicle.capacity_unit, 'lb')

    def test_driver_me_vehicle_patch_updates_fields(self):
        response = self.client.patch('/api/drivers/me/vehicle/', {
            'make': 'Chevrolet',
            'model': 'Express',
            'capacity': 2000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.make, 'Chevrolet')
        self.assertEqual(self.vehicle.model, 'Express')
        self.assertEqual(self.vehicle.capacity, 2000)

    def test_driver_me_vehicle_patch_mark_inactive(self):
        response = self.client.patch('/api/drivers/me/vehicle/', {
            'active': False,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['active'])
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.active)

    def test_driver_me_vehicle_deactivate_post(self):
        response = self.client.post('/api/drivers/me/vehicle/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['deactivated'])
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.active)

    def test_driver_cannot_reactivate_own_vehicle(self):
        self.vehicle.active = False
        self.vehicle.save(update_fields=['active'])
        response = self.client.patch('/api/drivers/me/vehicle/', {'active': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_driver_can_read_inactive_vehicle(self):
        self.vehicle.active = False
        self.vehicle.save(update_fields=['active'])
        response = self.client.get('/api/drivers/me/vehicle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['active'])

    def test_driver_cannot_edit_inactive_vehicle_details(self):
        deactivate = self.client.post('/api/drivers/me/vehicle/deactivate/')
        self.assertEqual(deactivate.status_code, status.HTTP_200_OK)
        response = self.client.patch('/api/drivers/me/vehicle/', {
            'model': 'Should Fail',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.vehicle.refresh_from_db()
        self.assertNotEqual(self.vehicle.model, 'Should Fail')

    def test_driver_cannot_delete_vehicle_via_admin_endpoint(self):
        response = self.client.delete(f'/api/vehicles/{self.vehicle.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_driver_cannot_staff_reactivate_endpoint(self):
        self.vehicle.active = False
        self.vehicle.save(update_fields=['active'])
        response = self.client.post(f'/api/vehicles/{self.vehicle.id}/reactivate/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_driver_patches_assigned_vehicle_via_vehicles_endpoint(self):
        response = self.client.patch(f'/api/vehicles/{self.vehicle.id}/', {
            'make': 'Chevrolet',
            'model': 'Express',
            'capacity': 2000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.make, 'Chevrolet')
        self.assertEqual(self.vehicle.model, 'Express')
        self.assertEqual(self.vehicle.capacity, 2000)

    def test_driver_cannot_patch_other_vehicle_via_vehicles_endpoint(self):
        other_vehicle = self.create_vehicle('other')
        response = self.client.patch(f'/api/vehicles/{other_vehicle.id}/', {
            'model': 'Hijacked',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_vehicle.refresh_from_db()
        self.assertNotEqual(other_vehicle.model, 'Hijacked')

    def test_driver_cannot_edit_inactive_vehicle_via_vehicles_endpoint(self):
        self.client.post('/api/drivers/me/vehicle/deactivate/')
        response = self.client.patch(f'/api/vehicles/{self.vehicle.id}/', {
            'model': 'Should Fail',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.vehicle.refresh_from_db()
        self.assertNotEqual(self.vehicle.model, 'Should Fail')

    def test_driver_can_get_assigned_vehicle_via_vehicles_endpoint(self):
        response = self.client.get(f'/api/vehicles/{self.vehicle.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_plate'], self.vehicle.license_plate)

    def test_driver_cannot_get_other_vehicle_via_vehicles_endpoint(self):
        other_vehicle = self.create_vehicle('hidden')
        response = self.client.get(f'/api/vehicles/{other_vehicle.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_reactivate_after_driver_deactivates(self):
        self.client.patch('/api/drivers/me/vehicle/', {'active': False}, format='json')
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.active)

        response = self.staff_client.post(f'/api/vehicles/{self.vehicle.id}/reactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertTrue(self.vehicle.active)

        read_back = self.client.get('/api/drivers/me/vehicle/')
        self.assertEqual(read_back.status_code, status.HTTP_200_OK)
        self.assertTrue(read_back.data['active'])

    def test_staff_sees_inactive_vehicle_in_list(self):
        self.client.patch('/api/drivers/me/vehicle/', {'active': False}, format='json')
        response = self.staff_client.get('/api/vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(v for v in response.data['results'] if v['id'] == self.vehicle.id)
        self.assertFalse(row['active'])


class DriverRegistrationWithVehicleTests(APITestCase, DriverVehicleCRUDFixtures):
    """Public driver registration creates driver + vehicle + assignment."""

    def test_register_creates_driver_and_vehicle(self):
        payload = {
            'username': 'reg_driver_1',
            'email': 'reg_driver_1@example.com',
            'password': 'testpass123',
            'first_name': 'Reg',
            'last_name': 'Driver',
            'phone_number': '5554443333',
            'license_number': 'DL-REG-001',
            'vehicle_license_plate': 'REG001',
            'vehicle_make': 'Toyota',
            'vehicle_model': 'Hiace',
            'vehicle_year': 2020,
            'vehicle_vin': '1REGTEST000000001',
            'vehicle_capacity': 1200,
            'vehicle_capacity_unit': 'kg',
        }
        client = APIClient()
        response = client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Driver.objects.filter(license_number='DL-REG-001').exists())
        self.assertTrue(Vehicle.objects.filter(license_plate='REG001').exists())
        driver = Driver.objects.get(license_number='DL-REG-001')
        self.assertTrue(DriverVehicle.objects.filter(driver=driver).exists())

    def test_register_rejects_duplicate_license_plate(self):
        Vehicle.objects.create(
            license_plate='DUPREG1',
            make='Ford',
            model='Transit',
            year=2021,
            vin='1DUPREGTEST00001',
            capacity=1000,
            capacity_unit='kg',
        )
        payload = {
            'username': 'reg_driver_2',
            'email': 'reg_driver_2@example.com',
            'password': 'testpass123',
            'first_name': 'Dup',
            'last_name': 'Driver',
            'phone_number': '5554443334',
            'license_number': 'DL-REG-002',
            'vehicle_license_plate': 'DUPREG1',
            'vehicle_make': 'Toyota',
            'vehicle_model': 'Hiace',
            'vehicle_year': 2020,
            'vehicle_vin': '1REGTEST000000002',
            'vehicle_capacity': 1200,
            'vehicle_capacity_unit': 'kg',
        }
        client = APIClient()
        response = client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
