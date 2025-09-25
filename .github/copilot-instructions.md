# DeliveryAppBackend Copilot Instructions

## Project Overview
Django REST API for managing package deliveries with complete self-registration workflow and JWT authentication. **WORKFLOW**: Drivers self-register with their vehicles → Customers register individually → Customers request deliveries from location A to location B. Core entities: `Customer`, `Delivery`, `Driver`, `Vehicle`, `DriverVehicle`, `DeliveryAssignment` with automatic driver-vehicle assignment logic.

## Architecture & Key Patterns

### Data Model Relationships
- `Delivery` -> `DeliveryAssignment` -> `Driver`/`Vehicle` (many-to-one assignments)
- `DriverVehicle` tracks temporal driver-vehicle assignments with date ranges
- Auto-assignment logic in `DeliveryAssignment.save()` finds current vehicle for driver

### Authentication & API Structure
- JWT tokens (15min access, 7-day refresh) with rotation enabled
- All ViewSets require `IsAuthenticated` permission class
- Base URL pattern: `/api/deliveries/` (ViewSet) + `/api/token/` (auth)

### Business Logic Conventions
- **Customer Registration**: Users must register/login before requesting deliveries
- `same_pickup_as_customer` boolean auto-sets `pickup_location = customer.address`
- `use_preferred_pickup` option uses customer's preferred pickup address
- Status choices: `Pending`, `En Route`, `Completed`, `Cancelled`
- Vehicle auto-assignment uses date-based queries for active `DriverVehicle` records
- Driver creation supports immediate vehicle assignment via specialized endpoints
- Vehicle capacity supports kg/lb units with display formatting

## Development Workflow

### Environment Setup
```powershell
# Start server (includes venv activation)
.\start-django.ps1

# Get auth token for testing
.\get-token-save.ps1  # Saves to last-token.txt

# Test API endpoints
.\test-api.ps1  # Uses saved token
```

### Database Configuration
- PostgreSQL only (`delivery_app` database, user: `delivery_user`)
- Required environment variables in `.env`: `SECRET_KEY`, `DATABASE_PASSWORD`
- Uses `python-decouple` for configuration management

### Mobile Development Notes
- `ALLOWED_HOSTS` includes `192.168.1.79` for mobile app testing
- API designed for mobile consumption with pagination (10 items/page)

## Key Files & Patterns

### Model Extensions
- `delivery/models.py`: Complex save() overrides for business logic
- Always check `DriverVehicle` date ranges when assigning vehicles
- Use `timezone.now().date()` for date comparisons in assignments

### API Patterns - Complete ViewSet Implementation
**CURRENT STATUS**: **✅ ALL VIEWSETS IMPLEMENTED** - Complete CRUD API available:
- `DeliveryViewSet` - with customer `request_delivery` endpoint
- `DriverViewSet` - with self-registration endpoint  
- `VehicleViewSet` - with capacity units (kg/lb)
- `DriverVehicleViewSet` - for vehicle assignments
- `DeliveryAssignmentViewSet` - for delivery assignments
- `CustomerViewSet` - with self-registration endpoint

**Pattern to follow for missing ViewSets**:

```python
# delivery/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Driver, Vehicle, DriverVehicle, DeliveryAssignment
from .serializers import DriverSerializer, VehicleSerializer, DriverVehicleSerializer, DeliveryAssignmentSerializer

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

class DriverVehicleViewSet(viewsets.ModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer
    permission_classes = [IsAuthenticated]

class DeliveryAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DeliveryAssignment.objects.all()
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsAuthenticated]
```

### Implemented Serializers - ✅ COMPLETE
**IMPLEMENTED**: All serializers available in `delivery/serializers.py`:
```python
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'phone_number', 'license_number', 'active']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'model', 'capacity', 'active']
```

### URL Registration - ✅ COMPLETE
**IMPLEMENTED**: All routes registered in `delivery/urls.py` router:
```python
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'driver-vehicles', DriverVehicleViewSet, basename='drivervehicle')
router.register(r'assignments', DeliveryAssignmentViewSet, basename='deliveryassignment')
```

## Driver-Vehicle Management

### Enhanced Driver Creation
The system supports two methods for driver creation:

1. **Standard Creation**: `POST /api/drivers/`
   - Creates driver without vehicle assignment
   - Vehicle can be assigned later via `assign_vehicle` action

2. **Driver + Vehicle Creation**: `POST /api/drivers/create_with_vehicle/`
   - Creates driver and assigns vehicle simultaneously
   - Requires `vehicle_id` in request payload
   - Automatically creates `DriverVehicle` assignment record

### Vehicle Assignment Endpoints
- `GET /api/drivers/creation_data/` - Lists available vehicles for forms
- `POST /api/drivers/{id}/assign_vehicle/` - Assign/reassign vehicle to existing driver
- `GET /api/vehicles/form_data/` - Provides capacity unit choices for vehicle forms
- Enhanced `DriverSerializer` includes current vehicle info in responses

### Serializer Features
- `DriverWithVehicleSerializer` for coupled creation with validation
- `DriverSerializer` shows `current_vehicle` and `current_vehicle_plate` read-only fields
- `VehicleSerializer` includes `capacity_display` with formatted units (kg/lb)
- Vehicle assignment respects temporal constraints (ends previous assignments)
- Capacity validation ensures reasonable values (1-50,000)

## Customer Registration System

### Customer Authentication Flow
1. **Registration**: `POST /api/customers/register/` (public endpoint)
   - Creates User account + Customer profile
   - Supports individual and business customers
   - Returns customer profile data

2. **Login**: `POST /api/token/` (existing JWT endpoint)
   - Customers use username/password to get JWT token
   - Same authentication system as staff users

3. **Delivery Request**: `POST /api/deliveries/request_delivery/`
   - Authenticated customers can request deliveries
   - Auto-assigns customer from JWT token
   - Supports pickup location preferences

### Customer Model Features
- **Individual Customers**: Personal deliveries with name/address
- **Business Customers**: Company deliveries with company name
- **Preferred Pickup Address**: Optional alternative pickup location
- **Address Auto-Assignment**: Uses customer address or preferred pickup
- **Profile Management**: Customers can view/edit their own profile

### Customer API Endpoints
- `POST /api/customers/register/` - Public registration (no auth required)
- `GET /api/customers/me/` - Get current customer profile
- `GET /api/customers/my_deliveries/` - Get customer's delivery history
- `POST /api/deliveries/request_delivery/` - Request new delivery
- `GET /api/deliveries/` - View own deliveries (filtered by customer)

### Security & Privacy
- Customers can only see their own deliveries and profile
- Staff users can see all customers and deliveries
- JWT authentication required for all delivery operations
- Customer profile linked to Django User model

## Testing Patterns

### Unit Testing Structure
Replace PowerShell testing with proper Django tests in `delivery/tests.py`:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from .models import Delivery, Driver, Vehicle, DriverVehicle, DeliveryAssignment

class DeliveryModelTests(TestCase):
    def test_same_pickup_as_customer_logic(self):
        """Test automatic pickup_location assignment"""
        delivery = Delivery.objects.create(
            customer_name="Test Customer",
            customer_address="123 Main St",
            dropoff_location="456 Oak Ave",
            same_pickup_as_customer=True
        )
        self.assertEqual(delivery.pickup_location, "123 Main St")

class DriverVehicleAssignmentTests(TestCase):
    def test_auto_vehicle_assignment(self):
        """Test DeliveryAssignment auto-assigns current vehicle"""
        driver = Driver.objects.create(name="Test Driver", license_number="DL123")
        vehicle = Vehicle.objects.create(license_plate="ABC123", model="Van", capacity=1000)
        
        # Create active assignment
        DriverVehicle.objects.create(
            driver=driver,
            vehicle=vehicle,
            assigned_from=timezone.now().date()
        )
        
        delivery = Delivery.objects.create(
            customer_name="Test",
            customer_address="123 Main St",
            dropoff_location="456 Oak Ave"
        )
        
        assignment = DeliveryAssignment.objects.create(
            delivery=delivery,
            driver=driver
            # vehicle should auto-assign
        )
        
        self.assertEqual(assignment.vehicle, vehicle)

class DeliveryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        
    def test_delivery_list_requires_auth(self):
        """Test API requires authentication"""
        response = self.client.get('/api/deliveries/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_authenticated_delivery_access(self):
        """Test authenticated access works"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/deliveries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Running Tests
```powershell
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test delivery

# Run with coverage (install coverage first)
pip install coverage
coverage run manage.py test
coverage report
```

## Driver-Vehicle Management

### Enhanced Driver Creation
The system supports two methods for driver creation:

1. **Standard Creation**: `POST /api/drivers/`
   - Creates driver without vehicle assignment
   - Vehicle can be assigned later via `assign_vehicle` action

2. **Driver + Vehicle Creation**: `POST /api/drivers/create_with_vehicle/`
   - Creates driver and assigns vehicle simultaneously
   - Requires `vehicle_id` in request payload
   - Automatically creates `DriverVehicle` assignment record

### Vehicle Assignment Endpoints
- `GET /api/drivers/creation_data/` - Lists available vehicles for forms
- `POST /api/drivers/{id}/assign_vehicle/` - Assign/reassign vehicle to existing driver
- `GET /api/vehicles/form_data/` - Provides capacity unit choices for vehicle forms
- Enhanced `DriverSerializer` includes current vehicle info in responses

### Serializer Features
- `DriverWithVehicleSerializer` for coupled creation with validation
- `DriverSerializer` shows `current_vehicle` and `current_vehicle_plate` read-only fields
- `VehicleSerializer` includes `capacity_display` with formatted units (kg/lb)
- Vehicle assignment respects temporal constraints (ends previous assignments)
- Capacity validation ensures reasonable values (1-50,000)

## Customer Registration System

### Customer Authentication Flow
1. **Registration**: `POST /api/customers/register/` (public endpoint)
   - Creates User account + Customer profile
   - Supports individual and business customers
   - Returns customer profile data

2. **Login**: `POST /api/token/` (existing JWT endpoint)
   - Customers use username/password to get JWT token
   - Same authentication system as staff users

3. **Delivery Request**: `POST /api/deliveries/request_delivery/`
   - Authenticated customers can request deliveries
   - Auto-assigns customer from JWT token
   - Supports pickup location preferences

### Customer Model Features
- **Individual Customers**: Personal deliveries with name/address
- **Business Customers**: Company deliveries with company name
- **Preferred Pickup Address**: Optional alternative pickup location
- **Address Auto-Assignment**: Uses customer address or preferred pickup
- **Profile Management**: Customers can view/edit their own profile

### Customer API Endpoints
- `POST /api/customers/register/` - Public registration (no auth required)
- `GET /api/customers/me/` - Get current customer profile
- `GET /api/customers/my_deliveries/` - Get customer's delivery history
- `POST /api/deliveries/request_delivery/` - Request new delivery
- `GET /api/deliveries/` - View own deliveries (filtered by customer)

### Security & Privacy
- Customers can only see their own deliveries and profile
- Staff users can see all customers and deliveries
- JWT authentication required for all delivery operations
- Customer profile linked to Django User model

## Database Migrations
- Date/time fields often added incrementally (see migration history)
- Status fields use choices for data integrity
- Foreign key relationships use `SET_NULL` for data preservation