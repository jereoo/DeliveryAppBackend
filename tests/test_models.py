"""
Comprehensive unit tests for DeliveryApp models
Target: 80% code coverage on core business logic
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from delivery.models import Customer, Driver, Vehicle, Delivery, DriverVehicle, DeliveryAssignment


class CustomerModelTests(TestCase):
    """Test Customer model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_individual_customer(self):
        """Test creating individual customer"""
        customer = Customer.objects.create(
            user=self.user,
            phone_number='555-1234',
            address='123 Main St',
            is_business=False
        )
        self.assertEqual(customer.user.username, 'testcustomer')
        self.assertFalse(customer.is_business)
        self.assertEqual(str(customer), 'testcustomer (test@example.com)')
    
    def test_create_business_customer(self):
        """Test creating business customer"""
        customer = Customer.objects.create(
            user=self.user,
            phone_number='555-1234',
            address='123 Business Ave',
            is_business=True,
            company_name='Test Company LLC'
        )
        self.assertTrue(customer.is_business)
        self.assertEqual(customer.company_name, 'Test Company LLC')
    
    def test_customer_str_representation(self):
        """Test customer string representation"""
        customer = Customer.objects.create(
            user=self.user,
            phone_number='555-1234',
            address='123 Main St'
        )
        self.assertEqual(str(customer), 'testcustomer (test@example.com)')


class DriverModelTests(TestCase):
    """Test Driver model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdriver',
            email='driver@example.com',
            password='testpass123',
            first_name='John',
            last_name='Driver'
        )
    
    def test_create_driver(self):
        """Test creating driver"""
        driver = Driver.objects.create(
            user=self.user,
            phone_number='555-5678',
            license_number='DL123456',
            active=True
        )
        self.assertEqual(driver.user.username, 'testdriver')
        self.assertEqual(driver.license_number, 'DL123456')
        self.assertTrue(driver.active)
    
    def test_driver_name_property(self):
        """Test driver name property from User model"""
        driver = Driver.objects.create(
            user=self.user,
            phone_number='555-5678',
            license_number='DL123456'
        )
        self.assertEqual(driver.full_name, 'John Driver')
    
    def test_driver_str_representation(self):
        """Test driver string representation"""
        driver = Driver.objects.create(
            user=self.user,
            phone_number='555-5678',
            license_number='DL123456'
        )
        self.assertEqual(str(driver), 'John Driver')


class VehicleModelTests(TestCase):
    """Test Vehicle model functionality"""
    
    def test_create_vehicle_kg(self):
        """Test creating vehicle with kg capacity"""
        vehicle = Vehicle.objects.create(
            license_plate='ABC123',
            make='Ford',
            model='Transit Van',
            year=2022,
            vin='1HGBH41JXMN109186',
            capacity=1000,
            capacity_unit='kg',
            active=True
        )
        self.assertEqual(vehicle.license_plate, 'ABC123')
        self.assertEqual(vehicle.capacity, 1000)
        self.assertEqual(vehicle.capacity_unit, 'kg')
        self.assertEqual(vehicle.capacity_display, '1000 Kilograms')
    
    def test_create_vehicle_lb(self):
        """Test creating vehicle with lb capacity"""
        vehicle = Vehicle.objects.create(
            license_plate='XYZ789',
            make='Chevrolet',
            model='Cargo Van',
            year=2020,
            vin='1GCWGBFG4L1234567',
            capacity=2200,
            capacity_unit='lb',
            active=True
        )
        self.assertEqual(vehicle.capacity_display, '2200 Pounds')
    
    def test_vehicle_str_representation(self):
        """Test vehicle string representation"""
        vehicle = Vehicle.objects.create(
            license_plate='ABC123',
            make='Ford',
            model='Transit Van',
            year=2019,
            vin='1FTBW2CM6HKA12345',
            capacity=1000
        )
        self.assertEqual(str(vehicle), 'Ford Transit Van (2019) - ABC123 - 1000kg')


class DeliveryModelTests(TestCase):
    """Test Delivery model functionality and business logic"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='555-1111',
            address_street='456 Customer St',
            address_city='Test City',
            address_state='Test State',
            address_postal_code='12345',
            address_country='US',
            preferred_pickup_address='789 Pickup Ave'
        )
    
    def test_create_basic_delivery(self):
        """Test creating basic delivery"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='123 Start St',
            dropoff_location='456 End Ave',
            item_description='Test package',
            status='Pending'
        )
        self.assertEqual(delivery.customer, self.customer)
        self.assertEqual(delivery.status, 'Pending')
        self.assertEqual(delivery.item_description, 'Test package')
    
    def test_delivery_same_pickup_as_customer(self):
        """Test same_pickup_as_customer logic"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='',  # Should be auto-filled
            dropoff_location='456 End Ave',
            item_description='Test package',
            same_pickup_as_customer=True
        )
        delivery.save()  # Trigger save() logic
        self.assertEqual(delivery.pickup_location, '456 Customer St, Test City, Test State, 12345, United States')
    
    def test_delivery_use_preferred_pickup(self):
        """Test use_preferred_pickup logic"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='',  # Should be auto-filled
            dropoff_location='456 End Ave',
            item_description='Test package',
            use_preferred_pickup=True
        )
        delivery.save()  # Trigger save() logic
        self.assertEqual(delivery.pickup_location, '789 Pickup Ave')
    
    def test_delivery_str_representation(self):
        """Test delivery string representation"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='123 Start St',
            dropoff_location='456 End Ave',
            item_description='Test package'
        )
        expected = f'Delivery {delivery.id} for customer1'
        self.assertEqual(str(delivery), expected)


class DriverVehicleModelTests(TestCase):
    """Test DriverVehicle assignment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='driver1',
            first_name='Test',
            last_name='Driver',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            phone_number='555-7777',
            license_number='DL789123'
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='TEST123',
            make='Test',
            model='Vehicle',
            year=2021,
            vin='1TEST123456789012',
            capacity=1500
        )
    
    def test_create_driver_vehicle_assignment(self):
        """Test creating driver-vehicle assignment"""
        assignment = DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date()
        )
        self.assertEqual(assignment.driver, self.driver)
        self.assertEqual(assignment.vehicle, self.vehicle)
        self.assertIsNotNone(assignment.assigned_from)
    
    def test_driver_vehicle_str_representation(self):
        """Test driver-vehicle string representation"""
        test_date = timezone.now().date()
        assignment = DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=test_date
        )
        expected = f'Test Driver -> TEST123 (from {test_date})'
        self.assertEqual(str(assignment), expected)


class DeliveryAssignmentModelTests(TestCase):
    """Test DeliveryAssignment model and auto-assignment logic"""
    
    def setUp(self):
        # Create customer
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone_number='555-1111',
            address='123 Customer St'
        )
        
        # Create driver
        self.driver_user = User.objects.create_user(
            username='driver1',
            first_name='Test',
            last_name='Driver',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='555-7777',
            license_number='DL789123'
        )
        
        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            license_plate='TEST123',
            make='Test',
            model='Vehicle',
            year=2021,
            vin='1TEST123456789013',
            capacity=1500
        )
        
        # Create delivery
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='123 Start St',
            dropoff_location='456 End Ave',
            item_description='Test package'
        )
    
    def test_create_delivery_assignment(self):
        """Test creating delivery assignment"""
        assignment = DeliveryAssignment.objects.create(
            delivery=self.delivery,
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_at=timezone.now()
        )
        self.assertEqual(assignment.delivery, self.delivery)
        self.assertEqual(assignment.driver, self.driver)
        self.assertEqual(assignment.vehicle, self.vehicle)
    
    def test_delivery_assignment_auto_vehicle(self):
        """Test automatic vehicle assignment when driver has active vehicle"""
        # Create active driver-vehicle assignment
        DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date()
        )
        
        # Create assignment without specifying vehicle
        assignment = DeliveryAssignment.objects.create(
            delivery=self.delivery,
            driver=self.driver,
            assigned_at=timezone.now()
        )
        
        # Vehicle should be auto-assigned
        assignment.save()  # Trigger save() logic
        self.assertEqual(assignment.vehicle, self.vehicle)
    
    def test_delivery_assignment_str_representation(self):
        """Test delivery assignment string representation"""
        assignment = DeliveryAssignment.objects.create(
            delivery=self.delivery,
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_at=timezone.now()
        )
        expected = f'Assignment for {self.delivery.id} to Test Driver'
        self.assertEqual(str(assignment), expected)


# Integration Tests
class DeliveryWorkflowIntegrationTests(TestCase):
    """Test complete delivery workflow integration"""
    
    def setUp(self):
        # Create customer with user
        self.customer_user = User.objects.create_user(
            username='integrationcustomer',
            email='integration@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone_number='555-9999',
            address='999 Integration St'
        )
        
        # Create driver with user
        self.driver_user = User.objects.create_user(
            username='integrationdriver',
            first_name='Integration',
            last_name='Driver',
            password='testpass123'
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='555-8888',
            license_number='INT123456'
        )
        
        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            license_plate='INT123',
            make='Integration',
            model='Vehicle',
            year=2022,
            vin='1INT123456789014',
            capacity=2000,
            capacity_unit='kg'
        )
    
    def test_complete_delivery_workflow(self):
        """Test complete end-to-end delivery workflow"""
        # Step 1: Assign vehicle to driver
        driver_vehicle = DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from=timezone.now().date()
        )
        
        # Step 2: Create delivery request
        delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='999 Integration St',
            dropoff_location='888 Destination Ave',
            item_description='Integration test package',
            same_pickup_as_customer=False,
            status='Pending'
        )
        
        # Step 3: Assign delivery to driver
        assignment = DeliveryAssignment.objects.create(
            delivery=delivery,
            driver=self.driver,
            assigned_at=timezone.now()
        )
        assignment.save()  # Trigger auto-vehicle assignment
        
        # Verify complete workflow
        self.assertEqual(assignment.vehicle, self.vehicle)
        self.assertEqual(delivery.status, 'Pending')
        self.assertTrue(DriverVehicle.objects.filter(driver=self.driver, vehicle=self.vehicle).exists())
        
        # Step 4: Update delivery status
        delivery.status = 'En Route'
        delivery.save()
        
        self.assertEqual(delivery.status, 'En Route')
        
        # Step 5: Complete delivery
        delivery.status = 'Completed'
        delivery.save()
        
        self.assertEqual(delivery.status, 'Completed')
        
        # Verify all relationships are intact
        self.assertEqual(delivery.customer, self.customer)
        self.assertEqual(assignment.driver, self.driver)
        self.assertEqual(assignment.vehicle, self.vehicle)