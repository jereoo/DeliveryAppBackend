from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from django.contrib.auth.models import User
from delivery.models import Driver, Vehicle, DriverVehicle, Delivery, DeliveryAssignment, Customer

class Command(BaseCommand):
    help = 'Load test data: 50 drivers (40 active), 50 vehicles (40 active), 200 deliveries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            DeliveryAssignment.objects.all().delete()
            DriverVehicle.objects.all().delete()
            Delivery.objects.all().delete()
            Customer.objects.all().delete()
            Driver.objects.all().delete()
            Vehicle.objects.all().delete()
            # Clear test users (keep superusers)
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

        # Create 50 drivers with User accounts (simulating self-registration)
        self.stdout.write('Creating 50 drivers with user accounts...')
        drivers = []
        driver_data = [
            ('driver.john.smith', 'John', 'Smith', 'john.smith@driver.com'),
            ('driver.maria.garcia', 'Maria', 'Garcia', 'maria.garcia@driver.com'),
            ('driver.david.johnson', 'David', 'Johnson', 'david.johnson@driver.com'),
            ('driver.lisa.chen', 'Lisa', 'Chen', 'lisa.chen@driver.com'),
            ('driver.michael.brown', 'Michael', 'Brown', 'michael.brown@driver.com'),
            ('driver.sarah.wilson', 'Sarah', 'Wilson', 'sarah.wilson@driver.com'),
            ('driver.robert.miller', 'Robert', 'Miller', 'robert.miller@driver.com'),
            ('driver.jennifer.davis', 'Jennifer', 'Davis', 'jennifer.davis@driver.com'),
            ('driver.william.rodriguez', 'William', 'Rodriguez', 'william.rodriguez@driver.com'),
            ('driver.jessica.martinez', 'Jessica', 'Martinez', 'jessica.martinez@driver.com'),
            ('driver.james.anderson', 'James', 'Anderson', 'james.anderson@driver.com'),
            ('driver.amanda.taylor', 'Amanda', 'Taylor', 'amanda.taylor@driver.com'),
            ('driver.christopher.thomas', 'Christopher', 'Thomas', 'christopher.thomas@driver.com'),
            ('driver.ashley.jackson', 'Ashley', 'Jackson', 'ashley.jackson@driver.com'),
            ('driver.daniel.white', 'Daniel', 'White', 'daniel.white@driver.com'),
            ('driver.michelle.harris', 'Michelle', 'Harris', 'michelle.harris@driver.com'),
            ('driver.matthew.martin', 'Matthew', 'Martin', 'matthew.martin@driver.com'),
            ('driver.laura.thompson', 'Laura', 'Thompson', 'laura.thompson@driver.com'),
            ('driver.anthony.garcia', 'Anthony', 'Garcia', 'anthony.garcia@driver.com'),
            ('driver.kimberly.lewis', 'Kimberly', 'Lewis', 'kimberly.lewis@driver.com'),
            ('driver.mark.lee', 'Mark', 'Lee', 'mark.lee@driver.com'),
            ('driver.donna.clark', 'Donna', 'Clark', 'donna.clark@driver.com'),
            ('driver.steven.robinson', 'Steven', 'Robinson', 'steven.robinson@driver.com'),
            ('driver.nancy.walker', 'Nancy', 'Walker', 'nancy.walker@driver.com'),
            ('driver.paul.hall', 'Paul', 'Hall', 'paul.hall@driver.com'),
            ('driver.karen.allen', 'Karen', 'Allen', 'karen.allen@driver.com'),
            ('driver.andrew.young', 'Andrew', 'Young', 'andrew.young@driver.com'),
            ('driver.lisa.king', 'Lisa', 'King', 'lisa.king@driver.com'),
            ('driver.joshua.wright', 'Joshua', 'Wright', 'joshua.wright@driver.com'),
            ('driver.betty.lopez', 'Betty', 'Lopez', 'betty.lopez@driver.com'),
            ('driver.kenneth.hill', 'Kenneth', 'Hill', 'kenneth.hill@driver.com'),
            ('driver.helen.scott', 'Helen', 'Scott', 'helen.scott@driver.com'),
            ('driver.brian.green', 'Brian', 'Green', 'brian.green@driver.com'),
            ('driver.dorothy.adams', 'Dorothy', 'Adams', 'dorothy.adams@driver.com'),
            ('driver.edward.baker', 'Edward', 'Baker', 'edward.baker@driver.com'),
            ('driver.sandra.gonzalez', 'Sandra', 'Gonzalez', 'sandra.gonzalez@driver.com'),
            ('driver.ronald.nelson', 'Ronald', 'Nelson', 'ronald.nelson@driver.com'),
            ('driver.carol.carter', 'Carol', 'Carter', 'carol.carter@driver.com'),
            ('driver.timothy.mitchell', 'Timothy', 'Mitchell', 'timothy.mitchell@driver.com'),
            ('driver.sharon.perez', 'Sharon', 'Perez', 'sharon.perez@driver.com'),
            ('driver.jason.roberts', 'Jason', 'Roberts', 'jason.roberts@driver.com'),
            ('driver.cynthia.turner', 'Cynthia', 'Turner', 'cynthia.turner@driver.com'),
            ('driver.jeffrey.phillips', 'Jeffrey', 'Phillips', 'jeffrey.phillips@driver.com'),
            ('driver.angela.campbell', 'Angela', 'Campbell', 'angela.campbell@driver.com'),
            ('driver.ryan.parker', 'Ryan', 'Parker', 'ryan.parker@driver.com'),
            ('driver.brenda.evans', 'Brenda', 'Evans', 'brenda.evans@driver.com'),
            ('driver.jacob.edwards', 'Jacob', 'Edwards', 'jacob.edwards@driver.com'),
            ('driver.emma.collins', 'Emma', 'Collins', 'emma.collins@driver.com'),
            ('driver.gary.stewart', 'Gary', 'Stewart', 'gary.stewart@driver.com'),
            ('driver.deborah.sanchez', 'Deborah', 'Sanchez', 'deborah.sanchez@driver.com')
        ]
        
        for i, (username, first_name, last_name, email) in enumerate(driver_data):
            active = i < 40  # First 40 are active
            
            # Create user account for driver (simulating self-registration)
            user = User.objects.create_user(
                username=username,
                email=email,
                password='driverpass123',
                first_name=first_name,
                last_name=last_name
            )
            
            driver = Driver.objects.create(
                user=user,
                name=f"{first_name} {last_name}",
                phone_number=f"555-{1000 + i:04d}",
                license_number=f"DL{10000 + i:05d}",
                active=active
            )
            drivers.append(driver)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(drivers)} drivers (40 active, 10 inactive)'))

        # Create 50 vehicles (40 active, 10 inactive)
        self.stdout.write('Creating 50 vehicles...')
        vehicles = []
        vehicle_models = [
            'Ford Transit', 'Mercedes Sprinter', 'Isuzu NPR', 'Chevrolet Express',
            'GMC Savana', 'Nissan NV200', 'Ram ProMaster', 'Ford E-Series',
            'Freightliner Sprinter', 'Iveco Daily', 'Peugeot Boxer', 'Fiat Ducato'
        ]
        
        for i in range(50):
            active = i < 40  # First 40 are active
            # Mix of kg and lb units for realistic data
            capacity_unit = 'kg' if i % 3 == 0 else 'lb'
            if capacity_unit == 'kg':
                capacity = random.choice([500, 750, 1000, 1250, 1500, 2000, 2500])
            else:  # lb
                capacity = random.choice([1100, 1650, 2200, 2750, 3300, 4400, 5500])
                
            vehicle = Vehicle.objects.create(
                license_plate=f"{chr(65 + i//10)}{chr(65 + (i%10)//5)}{chr(65 + i%5)}{1000 + i}",
                model=random.choice(vehicle_models),
                capacity=capacity,
                capacity_unit=capacity_unit,
                active=active
            )
            vehicles.append(vehicle)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(vehicles)} vehicles (40 active, 10 inactive)'))

        # Assign vehicles to active drivers
        self.stdout.write('Creating driver-vehicle assignments...')
        active_drivers = [d for d in drivers if d.active]
        active_vehicles = [v for v in vehicles if v.active]
        
        assignments_created = 0
        for i, driver in enumerate(active_drivers):
            if i < len(active_vehicles):  # Ensure we don't exceed available vehicles
                # Assign vehicle with start date in the past (1-30 days ago)
                assigned_from = timezone.now().date() - timedelta(days=random.randint(1, 30))
                DriverVehicle.objects.create(
                    driver=driver,
                    vehicle=active_vehicles[i],
                    assigned_from=assigned_from
                )
                assignments_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {assignments_created} driver-vehicle assignments'))

        # Create 30 customers (mix of individual and business customers)
        self.stdout.write('Creating 30 customers...')
        customers = []
        
        # Individual customers
        individual_customers = [
            ('john.smith', 'John', 'Smith', 'john.smith@email.com', '555-1001', '123 Main St, Downtown'),
            ('maria.garcia', 'Maria', 'Garcia', 'maria.garcia@email.com', '555-1002', '456 Oak Ave, Midtown'),
            ('david.johnson', 'David', 'Johnson', 'david.johnson@email.com', '555-1003', '789 Pine Rd, Eastside'),
            ('lisa.chen', 'Lisa', 'Chen', 'lisa.chen@email.com', '555-1004', '321 Elm Dr, Westside'),
            ('michael.brown', 'Michael', 'Brown', 'michael.brown@email.com', '555-1005', '654 Maple Way, Northside'),
            ('sarah.wilson', 'Sarah', 'Wilson', 'sarah.wilson@email.com', '555-1006', '987 Cedar Ln, Southside'),
            ('robert.miller', 'Robert', 'Miller', 'robert.miller@email.com', '555-1007', '147 Birch St, Central'),
            ('jennifer.davis', 'Jennifer', 'Davis', 'jennifer.davis@email.com', '555-1008', '258 Willow Ave, Riverside'),
            ('william.rodriguez', 'William', 'Rodriguez', 'william.rodriguez@email.com', '555-1009', '369 Spruce Rd, Hillside'),
            ('jessica.martinez', 'Jessica', 'Martinez', 'jessica.martinez@email.com', '555-1010', '159 Ash Dr, Lakeside'),
        ]
        
        # Business customers
        business_customers = [
            ('abc.corp', 'Admin', 'User', 'admin@abccorp.com', '555-2001', '100 Business Blvd, Downtown', 'ABC Corporation'),
            ('xyz.industries', 'Manager', 'XYZ', 'manager@xyzind.com', '555-2002', '200 Industrial Way, Eastside', 'XYZ Industries'),
            ('tech.solutions', 'IT', 'Manager', 'it@techsol.com', '555-2003', '300 Tech Park Dr, Westside', 'Tech Solutions Inc'),
            ('global.logistics', 'Logistics', 'Coord', 'coord@globallog.com', '555-2004', '400 Shipping Ave, Southside', 'Global Logistics'),
            ('metro.hospital', 'Admin', 'Staff', 'admin@metrohospital.com', '555-2005', '500 Health St, Central', 'Metro Hospital'),
            ('city.university', 'Facilities', 'Manager', 'facilities@cityuni.edu', '555-2006', '600 Campus Dr, Northside', 'City University'),
            ('downtown.hotel', 'Front', 'Desk', 'frontdesk@downtownhotel.com', '555-2007', '700 Hotel Blvd, Downtown', 'Downtown Hotel'),
            ('shopping.center', 'Operations', 'Manager', 'ops@shoppingcenter.com', '555-2008', '800 Mall Way, Midtown', 'Shopping Center'),
            ('retail.chain', 'Store', 'Manager', 'manager@retailchain.com', '555-2009', '900 Retail Ave, Eastside', 'Retail Chain'),
            ('manufacturing.co', 'Plant', 'Manager', 'manager@manufacturing.com', '555-2010', '1000 Factory Rd, Westside', 'Manufacturing Co'),
        ]
        
        # Create individual customers
        for username, first_name, last_name, email, phone, address in individual_customers:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=first_name,
                last_name=last_name
            )
            customer = Customer.objects.create(
                user=user,
                phone_number=phone,
                address=address,
                is_business=False
            )
            customers.append(customer)
        
        # Create business customers
        for username, first_name, last_name, email, phone, address, company_name in business_customers:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=first_name,
                last_name=last_name
            )
            customer = Customer.objects.create(
                user=user,
                phone_number=phone,
                address=address,
                company_name=company_name,
                is_business=True,
                preferred_pickup_address=f"{address} - Loading Dock" if random.choice([True, False]) else None
            )
            customers.append(customer)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(customers)} customers (10 individual, 10 business)'))

        # Create 200 deliveries
        self.stdout.write('Creating 200 deliveries...')
        
        addresses = [
            '123 Main St, Downtown', '456 Oak Ave, Midtown', '789 Pine Rd, Eastside',
            '321 Elm Dr, Westside', '654 Maple Way, Northside', '987 Cedar Ln, Southside',
            '147 Birch St, Central', '258 Willow Ave, Riverside', '369 Spruce Rd, Hillside',
            '159 Ash Dr, Lakeside', '753 Poplar Way, Seaside', '951 Fir Ln, Mountainside'
        ]
        
        items = [
            'Office Furniture', 'Medical Equipment', 'Electronic Devices', 'Documents Package',
            'Laboratory Supplies', 'Computer Hardware', 'Marketing Materials', 'Legal Documents',
            'Pharmaceutical Products', 'Automotive Parts', 'Construction Materials', 'Food Supplies',
            'Textile Products', 'Artwork', 'Books and Manuals', 'Industrial Tools'
        ]

        deliveries = []
        today = timezone.now().date()
        
        for i in range(200):
            # Determine status and dates based on requirements
            if i < 100:  # 100 completed
                status = 'Completed'
                delivery_date = today - timedelta(days=random.randint(1, 30))
            elif i < 130:  # 30 en route  
                status = 'En Route'
                delivery_date = today
            else:  # 70 pending (scheduled to start)
                status = 'Pending'
                delivery_date = today + timedelta(days=random.randint(1, 15))
            
            customer = random.choice(customers)
            same_pickup = random.choice([True, False])
            use_preferred = random.choice([True, False]) if customer.preferred_pickup_address else False
            
            delivery = Delivery.objects.create(
                customer=customer,
                pickup_location=random.choice(addresses) if not same_pickup and not use_preferred else '',
                dropoff_location=random.choice(addresses),
                same_pickup_as_customer=same_pickup,
                use_preferred_pickup=use_preferred,
                item_description=random.choice(items),
                status=status,
                delivery_date=delivery_date,
                delivery_time=timezone.now().time().replace(
                    hour=random.randint(8, 17),
                    minute=random.choice([0, 15, 30, 45])
                ),
                special_instructions=random.choice([
                    None, "Fragile items - handle with care", "Call before delivery", 
                    "Loading dock delivery", "Signature required", "Ground floor only"
                ]),
                estimated_cost=random.uniform(25.0, 150.0)
            )
            deliveries.append(delivery)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(deliveries)} deliveries'))

        # Create delivery assignments for active deliveries
        self.stdout.write('Creating delivery assignments...')
        active_deliveries = [d for d in deliveries if d.status in ['En Route', 'Completed']]
        assignment_count = 0
        
        for delivery in active_deliveries:
            # Assign to random active driver
            driver = random.choice(active_drivers)
            assignment = DeliveryAssignment.objects.create(
                delivery=delivery,
                driver=driver
                # Vehicle will be auto-assigned via the model's save() method
            )
            assignment_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {assignment_count} delivery assignments'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DATABASE LOADED SUCCESSFULLY'))
        self.stdout.write('='*50)
        self.stdout.write(f'Users: {User.objects.count()} total ({User.objects.filter(is_superuser=False).count()} customers)')
        self.stdout.write(f'Customers: {Customer.objects.count()} total ({Customer.objects.filter(is_business=True).count()} business, {Customer.objects.filter(is_business=False).count()} individual)')
        self.stdout.write(f'Drivers: {Driver.objects.count()} total ({Driver.objects.filter(active=True).count()} active)')
        self.stdout.write(f'Vehicles: {Vehicle.objects.count()} total ({Vehicle.objects.filter(active=True).count()} active)')
        self.stdout.write(f'Driver-Vehicle Assignments: {DriverVehicle.objects.count()}')
        self.stdout.write(f'Deliveries: {Delivery.objects.count()} total')
        self.stdout.write(f'  - Completed: {Delivery.objects.filter(status="Completed").count()}')
        self.stdout.write(f'  - En Route: {Delivery.objects.filter(status="En Route").count()}')
        self.stdout.write(f'  - Pending: {Delivery.objects.filter(status="Pending").count()}')
        self.stdout.write(f'Delivery Assignments: {DeliveryAssignment.objects.count()}')
        self.stdout.write('='*50)