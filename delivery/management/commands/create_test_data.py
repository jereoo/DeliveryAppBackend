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
            default=100,
            help='Number of customers to create (default: 100, split between CA and US)'
        )
        parser.add_argument(
            '--drivers',
            type=int,
            default=20,
            help='Number of drivers to create (default: 20)'
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
        """Create test customers with realistic country-specific addresses"""
        
        # Sample customer data
        first_names = [
            'John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily',
            'Michael', 'Ashley', 'Chris', 'Jessica', 'Daniel', 'Amanda', 'James',
            'Emma', 'William', 'Olivia', 'Noah', 'Ava', 'Liam', 'Sophia', 'Mason'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Taylor', 'Thomas', 'Jackson', 'White', 'Harris'
        ]
        
        # Canadian data
        canadian_streets = [
            'King St', 'Queen St', 'Yonge St', 'Bay St', 'Dundas St', 'College St',
            'Bloor St', 'Eglinton Ave', 'Sheppard Ave', 'Lawrence Ave', 'York Mills Rd'
        ]
        
        canadian_cities = [
            {'city': 'Toronto', 'province': 'ON'},
            {'city': 'Vancouver', 'province': 'BC'},
            {'city': 'Montreal', 'province': 'QC'},
            {'city': 'Calgary', 'province': 'AB'},
            {'city': 'Ottawa', 'province': 'ON'},
            {'city': 'Edmonton', 'province': 'AB'},
            {'city': 'Mississauga', 'province': 'ON'},
            {'city': 'Winnipeg', 'province': 'MB'},
            {'city': 'Hamilton', 'province': 'ON'},
            {'city': 'Quebec City', 'province': 'QC'}
        ]
        
        # US data
        us_streets = [
            'Main St', 'Oak Ave', 'Pine Rd', 'Elm Dr', 'Maple Ln', 'Cedar Blvd',
            'Washington St', 'First Ave', 'Second St', 'Park Ave', 'Broadway',
            'Market St', 'Church St', 'School Rd', 'Mill St'
        ]
        
        us_cities = [
            {'city': 'Springfield', 'state': 'IL'},
            {'city': 'Franklin', 'state': 'TN'},
            {'city': 'Georgetown', 'state': 'TX'},
            {'city': 'Madison', 'state': 'WI'},
            {'city': 'Riverside', 'state': 'CA'},
            {'city': 'Fairview', 'state': 'NJ'},
            {'city': 'Arlington', 'state': 'VA'},
            {'city': 'Salem', 'state': 'OR'},
            {'city': 'Clinton', 'state': 'NY'},
            {'city': 'Monroe', 'state': 'LA'}
        ]
        
        company_names = [
            'TechCorp Solutions', 'Global Industries', 'Metro Services',
            'Prime Business Group', 'Advanced Systems LLC', 'Digital Innovations',
            'Maple Leaf Enterprises', 'Northern Solutions', 'Pacific Coast Corp',
            'Atlantic Services', 'Prairie Industries', 'Mountain View LLC'
        ]

        # Create half Canadian, half US customers
        canadian_count = count // 2
        us_count = count - canadian_count

        self.stdout.write(f"Creating {canadian_count} Canadian customers and {us_count} US customers...")

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
            
            # Determine country (first half Canadian, second half US)
            if i < canadian_count:
                country = 'CA'
                street = random.choice(canadian_streets)
                city_info = random.choice(canadian_cities)
                city = city_info['city']
                state_province = city_info['province']
                
                # Generate Canadian postal code (A1A 1A1 format)
                def generate_canadian_postal():
                    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    digits = '0123456789'
                    return f"{random.choice(letters)}{random.choice(digits)}{random.choice(letters)} {random.choice(digits)}{random.choice(letters)}{random.choice(digits)}"
                
                postal_code = generate_canadian_postal()
                phone_prefix = random.choice(['416', '647', '437', '905', '289', '365'])  # Canadian area codes
                
            else:
                country = 'US'
                street = random.choice(us_streets)
                city_info = random.choice(us_cities)
                city = city_info['city']
                state_province = city_info['state']
                
                # Generate US ZIP code (12345 or 12345-1234 format)
                zip_base = f"{random.randint(10000, 99999)}"
                postal_code = zip_base if random.random() < 0.5 else f"{zip_base}-{random.randint(1000, 9999)}"
                phone_prefix = random.choice(['555', '212', '415', '702', '305'])  # US area codes
            
            # Generate address components
            street_number = random.randint(100, 9999)
            unit = f"Apt {random.randint(1, 999)}" if random.random() < 0.3 else ""
            
            phone_number = f"{phone_prefix}-{random.randint(100,999)}-{random.randint(1000,9999)}"
            
            # Create Customer profile with separated address fields
            if is_business:
                company_name = random.choice(company_names)
                customer = Customer.objects.create(
                    user=user,
                    is_business=True,
                    company_name=f"{company_name} #{i+1}",
                    phone_number=phone_number,
                    address_unit=unit,
                    address_street=f"{street_number} {street}",
                    address_city=city,
                    address_state=state_province,
                    address_postal_code=postal_code,
                    address_country=country
                )
            else:
                customer = Customer.objects.create(
                    user=user,
                    is_business=False,
                    phone_number=phone_number,
                    address_unit=unit,
                    address_street=f"{street_number} {street}",
                    address_city=city,
                    address_state=state_province,
                    address_postal_code=postal_code,
                    address_country=country
                )

            # 40% chance of having preferred pickup address
            if random.random() < 0.4:
                pickup_street = random.choice(canadian_streets if country == 'CA' else us_streets)
                pickup_number = random.randint(100, 9999)
                customer.preferred_pickup_address = f"{pickup_number} {pickup_street}, {city}, {state_province}"
                customer.save()

            country_name = "Canada" if country == 'CA' else "United States"
            customer_type = 'Business' if is_business else 'Individual'
            self.stdout.write(f"Created {country_name} customer: {username} ({customer_type}) - {postal_code}")

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