# delivery/management/commands/create_test_data.py
"""
Django management command to create test data for mobile app testing.
Usage: python manage.py create_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from delivery.models import Customer, Driver, Vehicle, DriverVehicle
from django.utils import timezone
from datetime import date
import random


class Command(BaseCommand):
    help = 'Create test customers and drivers for mobile app testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customers',
            type=int,
            default=10,
            help='Number of customers to create (default: 10)'
        )
        parser.add_argument(
            '--drivers',
            type=int,
            default=10,
            help='Number of drivers to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing test data...'))
            # Clear test data (keep superusers)
            User.objects.filter(is_superuser=False).delete()
            Customer.objects.all().delete()
            Driver.objects.all().delete()
            Vehicle.objects.all().delete()
            DriverVehicle.objects.all().delete()

        # Create test customers
        customers_count = options['customers']
        drivers_count = options['drivers']

        self.stdout.write(f'Creating {customers_count} test customers...')
        self.create_test_customers(customers_count)

        self.stdout.write(f'Creating {drivers_count} test drivers with vehicles...')
        self.create_test_drivers(drivers_count)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {customers_count} customers and {drivers_count} drivers!'
            )
        )

    def create_test_customers(self, count):
        """Create test customers with realistic data"""
        
        # Sample customer data
        first_names = [
            'John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily',
            'Michael', 'Ashley', 'Chris', 'Jessica', 'Daniel', 'Amanda', 'James'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez'
        ]
        
        streets = [
            'Main St', 'Oak Ave', 'Pine Rd', 'Elm Dr', 'Maple Ln', 'Cedar Blvd',
            'Washington St', 'First Ave', 'Second St', 'Park Ave', 'Broadway',
            'Market St', 'Church St', 'School Rd', 'Mill St'
        ]
        
        cities = ['Springfield', 'Franklin', 'Georgetown', 'Madison', 'Riverside']
        
        company_names = [
            'TechCorp Solutions', 'Global Industries', 'Metro Services',
            'Prime Business Group', 'Advanced Systems LLC', 'Digital Innovations'
        ]

        for i in range(count):
            # Create User account
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}.{i+1}"
            email = f"{username}@email.com"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',  # Default password for testing
                first_name=first_name,
                last_name=last_name
            )

            # Decide if business or individual (30% business, 70% individual)
            is_business = random.random() < 0.3
            
            # Generate address
            street_number = random.randint(100, 9999)
            street = random.choice(streets)
            city = random.choice(cities)
            address = f"{street_number} {street}, {city}, State 12345"
            
            # Create Customer profile
            if is_business:
                company_name = random.choice(company_names)
                customer = Customer.objects.create(
                    user=user,
                    is_business=True,
                    company_name=f"{company_name} #{i+1}",
                    address=address,
                    phone_number=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}"
                )
            else:
                customer = Customer.objects.create(
                    user=user,
                    is_business=False,
                    address=address,
                    phone_number=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}"
                )

            # 40% chance of having preferred pickup address
            if random.random() < 0.4:
                pickup_street = random.choice(streets)
                pickup_address = f"{random.randint(100,9999)} {pickup_street}, {city}, State 12345"
                customer.preferred_pickup_address = pickup_address
                customer.save()

            self.stdout.write(f"Created customer: {username} ({'Business' if is_business else 'Individual'})")

    def create_test_drivers(self, count):
        """Create test drivers with assigned vehicles"""
        
        driver_names = [
            'Alex Johnson', 'Maria Garcia', 'Kevin Brown', 'Linda Davis',
            'Carlos Rodriguez', 'Jennifer Wilson', 'Mark Thompson', 'Amy Lee',
            'Tony Martinez', 'Rachel Green', 'Steve Clark', 'Diana Lopez',
            'Paul Anderson', 'Sandra White', 'Ryan Taylor'
        ]
        
        vehicle_makes = ['Ford', 'Chevrolet', 'Toyota', 'Honda', 'Nissan', 'Hyundai']
        vehicle_models = {
            'Ford': ['Transit', 'E-Series', 'F-150'],
            'Chevrolet': ['Express', 'Silverado', 'Colorado'],
            'Toyota': ['Hiace', 'Tacoma', 'Sienna'],
            'Honda': ['Pilot', 'Ridgeline', 'Odyssey'],
            'Nissan': ['NV200', 'Frontier', 'Titan'],
            'Hyundai': ['H350', 'Santa Fe', 'Tucson']
        }

        for i in range(count):
            # Create Driver
            name = random.choice(driver_names) if i < len(driver_names) else f"Driver {i+1}"
            license_number = f"DL{random.randint(100000, 999999)}"
            phone = f"555-{random.randint(100,999)}-{random.randint(1000,9999)}"
            
            driver = Driver.objects.create(
                name=name,
                phone_number=phone,
                license_number=license_number,
                active=True
            )

            # Create Vehicle for the driver
            make = random.choice(vehicle_makes)
            model = random.choice(vehicle_models[make])
            license_plate = f"{random.choice(['ABC', 'XYZ', 'DEF'])}{random.randint(100, 999)}"
            capacity = random.choice([500, 750, 1000, 1250, 1500, 2000])  # kg
            
            vehicle = Vehicle.objects.create(
                license_plate=license_plate,
                model=f"{make} {model}",
                capacity=capacity,
                active=True
            )

            # Assign vehicle to driver (current assignment)
            DriverVehicle.objects.create(
                driver=driver,
                vehicle=vehicle,
                assigned_from=date.today()
                # assigned_to is None for current assignment
            )

            self.stdout.write(
                f"Created driver: {name} with {vehicle.model} ({license_plate}) - {capacity}kg capacity"
            )

    def create_sample_deliveries(self, count=5):
        """Create sample delivery requests for testing"""
        # This could be extended to create sample deliveries
        pass