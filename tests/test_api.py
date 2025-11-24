"""
Integration tests for API endpoints and authentication
Target: Test all REST API functionality and JWT flows
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from delivery.models import Customer, Driver, Vehicle, Delivery


class AuthenticationAPITests(APITestCase):
    """Test JWT authentication flows"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_token_obtain(self):
        """Test JWT token creation"""
        url = '/api/token/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        refresh = RefreshToken.for_user(self.user)
        url = '/api/token/refresh/'
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        url = '/api/customers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = '/api/customers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomerAPITests(APITestCase):
    """Test Customer API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='555-1234',
            address_street='123 Test St',
            address_city='Test City',
            address_state='Test State',
            address_postal_code='12345',
            address_country='US'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_customer_list(self):
        """Test customer list endpoint"""
        url = '/api/customers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_customer_detail(self):
        """Test customer detail endpoint"""
        url = f'/api/customers/{self.customer.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '555-1234')
    
    def test_customer_registration(self):
        """Test customer registration endpoint"""
        url = '/api/customers/register/'
        data = {
            'username': 'newcustomer',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'Customer',
            'phone_number': '555-5678',
            'address_street': '456 New St',
            'address_city': 'Test City',
            'address_state': 'Test State',
            'address_postal_code': '12345',
            'address_country': 'US',
            'is_business': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newcustomer').exists())
        self.assertTrue(Customer.objects.filter(phone_number='555-5678').exists())


class DriverAPITests(APITestCase):
    """Test Driver API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdriver',
            first_name='Test',
            last_name='Driver',
            email='driver@example.com',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            name='Test Driver',
            phone_number='555-7777',
            license_number='DL123456'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_driver_list(self):
        """Test driver list endpoint"""
        url = '/api/drivers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_driver_detail(self):
        """Test driver detail endpoint"""
        url = f'/api/drivers/{self.driver.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_number'], 'DL123456')
    
    def test_driver_create(self):
        """Test driver creation endpoint"""
        new_user = User.objects.create_user(
            username='newdriver',
            first_name='New',
            last_name='Driver',
            password='newpass123'
        )
        url = '/api/drivers/'
        data = {
            'user': new_user.id,
            'first_name': 'Test',
            'last_name': 'New Driver',
            'phone_number': '555-9999',
            'license_number': 'DL999888',
            'active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Driver.objects.filter(license_number='DL999888').exists())


class VehicleAPITests(APITestCase):
    """Test Vehicle API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='TEST123',
            make='Test',
            model='Vehicle',
            year=2021,
            vin='1TEST123456789015',
            capacity=1500,
            capacity_unit='kg'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_vehicle_list(self):
        """Test vehicle list endpoint"""
        url = '/api/vehicles/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_vehicle_detail(self):
        """Test vehicle detail endpoint"""
        url = f'/api/vehicles/{self.vehicle.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_plate'], 'TEST123')
        self.assertEqual(response.data['capacity_display'], '1500 Kilograms')
    
    def test_vehicle_create(self):
        """Test vehicle creation endpoint"""
        url = '/api/vehicles/'
        data = {
            'license_plate': 'NEW456',
            'make': 'Ford',
            'model': 'Transit',
            'year': 2023,
            'vin': 'NEW12345678901234',
            'capacity': 2000,
            'capacity_unit': 'lb',
            'active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vehicle.objects.filter(license_plate='NEW456').exists())
        
        # Verify capacity display
        new_vehicle = Vehicle.objects.get(license_plate='NEW456')
        self.assertEqual(new_vehicle.capacity_display, '2000 Pounds')


class DeliveryAPITests(APITestCase):
    """Test Delivery API endpoints"""
    
    def setUp(self):
        # Create customer
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone_number='555-1111',
            address_street='123 Customer St',
            address_city='Test City',
            address_state='Test State',
            address_postal_code='12345',
            address_country='US'
        )
        
        # Create delivery
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='123 Start St',
            dropoff_location='456 End Ave',
            item_description='Test package'
        )
        
        refresh = RefreshToken.for_user(self.customer_user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_delivery_list(self):
        """Test delivery list endpoint"""
        url = '/api/deliveries/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_delivery_detail(self):
        """Test delivery detail endpoint"""
        url = f'/api/deliveries/{self.delivery.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_description'], 'Test package')
    
    def test_delivery_request(self):
        """Test customer delivery request endpoint"""
        url = '/api/deliveries/request_delivery/'
        data = {
            'pickup_location': '789 New Start St',
            'dropoff_location': '321 New End Ave',
            'item_description': 'New test package',
            'same_pickup_as_customer': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Delivery.objects.filter(item_description='New test package').exists())
    
    def test_delivery_request_same_pickup_as_customer(self):
        """Test delivery request with same pickup as customer address"""
        url = '/api/deliveries/request_delivery/'
        data = {
            'pickup_location': '',  # Should be auto-filled
            'dropoff_location': '321 New End Ave',
            'item_description': 'Auto pickup test',
            'same_pickup_as_customer': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify pickup location was auto-filled
        new_delivery = Delivery.objects.get(item_description='Auto pickup test')
        self.assertEqual(new_delivery.pickup_location, '123 Customer St, Test City, Test State, 12345, United States')


class APIErrorHandlingTests(APITestCase):
    """Test API error handling and validation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_invalid_token(self):
        """Test API response to invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        url = '/api/customers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_missing_required_fields(self):
        """Test API validation for missing required fields"""
        url = '/api/vehicles/'
        data = {
            'model': 'Incomplete Vehicle'
            # Missing license_plate and capacity
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('license_plate', response.data)
    
    def test_duplicate_license_plate(self):
        """Test vehicle creation with duplicate license plate"""
        # Create first vehicle
        Vehicle.objects.create(
            license_plate='DUPLICATE',
            make='First',
            model='Vehicle',
            year=2020,
            vin='1DUPLICATE123456',
            capacity=1000
        )
        
        # Try to create second vehicle with same license plate
        url = '/api/vehicles/'
        data = {
            'license_plate': 'DUPLICATE',
            'model': 'Second Vehicle',
            'capacity': 2000,
            'capacity_unit': 'kg'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_nonexistent_resource(self):
        """Test accessing non-existent resource"""
        url = '/api/customers/99999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class APIPaginationTests(APITestCase):
    """Test API pagination functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Create multiple customers for pagination testing
        for i in range(15):
            user = User.objects.create_user(
                username=f'customer{i}',
                password='testpass123'
            )
            Customer.objects.create(
                user=user,
                phone_number=f'555-{1000+i}',
                address_street=f'{i} Test St',
                address_city='Test City',
                address_state='Test State',
                address_postal_code='12345',
                address_country='US'
            )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_pagination_first_page(self):
        """Test first page of paginated results"""
        url = '/api/customers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
    
    def test_pagination_second_page(self):
        """Test second page of paginated results"""
        url = '/api/customers/?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Remaining results
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])