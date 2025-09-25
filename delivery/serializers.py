# delivery/serializers.py
from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User
from .models import Delivery, Driver, Vehicle, DriverVehicle, DeliveryAssignment, Customer

class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    display_name = serializers.CharField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'display_name', 
                 'phone_number', 'address', 'company_name', 'is_business', 'preferred_pickup_address', 
                 'created_at', 'active']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True, min_length=8)
    first_name = serializers.CharField(source='user.first_name', required=True, help_text="Customer's first name")
    last_name = serializers.CharField(source='user.last_name', required=True, help_text="Customer's last name")
    
    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                 'phone_number', 'address', 'company_name', 'is_business', 'preferred_pickup_address']
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        # Create User
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        # Create Customer profile
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


class DeliverySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.display_name', read_only=True)
    customer_email = serializers.EmailField(source='customer.user.email', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    
    class Meta:
        model = Delivery
        fields = ['id', 'customer', 'customer_name', 'customer_email', 'customer_phone',
                 'pickup_location', 'dropoff_location', 'same_pickup_as_customer', 'use_preferred_pickup', 'same_dropoff_as_customer',
                 'item_description', 'status', 'delivery_date', 'delivery_time', 'special_instructions',
                 'estimated_cost', 'created_at', 'updated_at']


class DeliveryCreateSerializer(serializers.ModelSerializer):
    """Serializer for customer creating their own delivery"""
    pickup_location = serializers.CharField(required=False, allow_blank=True, help_text="Pickup address (auto-filled if same_pickup_as_customer is True)")
    dropoff_location = serializers.CharField(required=False, allow_blank=True, help_text="Dropoff address (auto-filled if same_dropoff_as_customer is True)")
    
    class Meta:
        model = Delivery
        fields = ['pickup_location', 'dropoff_location', 'same_pickup_as_customer', 'use_preferred_pickup', 'same_dropoff_as_customer',
                 'item_description', 'delivery_date', 'delivery_time', 'special_instructions']
    
    def validate(self, data):
        """Ensure pickup and dropoff locations are provided unless using customer address"""
        errors = {}
        
        # Validate pickup location
        if not data.get('same_pickup_as_customer') and not data.get('use_preferred_pickup') and not data.get('pickup_location'):
            errors['pickup_location'] = 'This field is required when not using customer address as pickup location.'
        
        # Validate dropoff location
        if not data.get('same_dropoff_as_customer') and not data.get('dropoff_location'):
            errors['dropoff_location'] = 'This field is required when not using customer address as dropoff location.'
            
        if errors:
            raise serializers.ValidationError(errors)
            
        return data
    
    def create(self, validated_data):
        # Auto-assign customer from request user
        customer = self.context['request'].user.customer_profile
        validated_data['customer'] = customer
        return super().create(validated_data)


class DriverSerializer(serializers.ModelSerializer):
    # Optional vehicle assignment fields
    vehicle_id = serializers.IntegerField(write_only=True, required=False, help_text="ID of vehicle to assign to this driver")
    assigned_from = serializers.DateField(write_only=True, required=False, help_text="Date when vehicle assignment starts (defaults to today)")
    
    # Read-only fields to show current vehicle assignment
    current_vehicle = serializers.SerializerMethodField(read_only=True)
    current_vehicle_plate = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Driver
        fields = ['id', 'name', 'phone_number', 'license_number', 'active', 
                 'vehicle_id', 'assigned_from', 'current_vehicle', 'current_vehicle_plate']
    
    def get_current_vehicle(self, obj):
        """Get the currently assigned vehicle ID"""
        from django.utils import timezone
        today = timezone.now().date()
        current_assignment = DriverVehicle.objects.filter(
            driver=obj,
            assigned_from__lte=today
        ).filter(
            models.Q(assigned_to__isnull=True) | models.Q(assigned_to__gte=today)
        ).order_by('-assigned_from').first()
        
        return current_assignment.vehicle.id if current_assignment and current_assignment.vehicle else None
    
    def get_current_vehicle_plate(self, obj):
        """Get the currently assigned vehicle license plate"""
        from django.utils import timezone
        today = timezone.now().date()
        current_assignment = DriverVehicle.objects.filter(
            driver=obj,
            assigned_from__lte=today
        ).filter(
            models.Q(assigned_to__isnull=True) | models.Q(assigned_to__gte=today)
        ).order_by('-assigned_from').first()
        
        return current_assignment.vehicle.license_plate if current_assignment and current_assignment.vehicle else None
    
    def create(self, validated_data):
        from django.utils import timezone
        
        # Extract vehicle assignment data
        vehicle_id = validated_data.pop('vehicle_id', None)
        assigned_from = validated_data.pop('assigned_from', timezone.now().date())
        
        # Create the driver
        driver = Driver.objects.create(**validated_data)
        
        # Create vehicle assignment if vehicle_id provided
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id, active=True)
                DriverVehicle.objects.create(
                    driver=driver,
                    vehicle=vehicle,
                    assigned_from=assigned_from
                )
            except Vehicle.DoesNotExist:
                # If vehicle doesn't exist, still create driver but raise warning
                pass
        
        return driver
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        # Extract vehicle assignment data
        vehicle_id = validated_data.pop('vehicle_id', None)
        assigned_from = validated_data.pop('assigned_from', timezone.now().date())
        
        # Update driver fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle vehicle assignment update
        if vehicle_id is not None:
            # End current assignment if exists
            today = timezone.now().date()
            current_assignments = DriverVehicle.objects.filter(
                driver=instance,
                assigned_to__isnull=True
            )
            for assignment in current_assignments:
                assignment.assigned_to = today
                assignment.save()
            
            # Create new assignment if vehicle_id > 0
            if vehicle_id > 0:
                try:
                    vehicle = Vehicle.objects.get(id=vehicle_id, active=True)
                    DriverVehicle.objects.create(
                        driver=instance,
                        vehicle=vehicle,
                        assigned_from=assigned_from
                    )
                except Vehicle.DoesNotExist:
                    pass
        
        return instance


class VehicleSerializer(serializers.ModelSerializer):
    capacity_display = serializers.CharField(read_only=True, help_text="Formatted capacity with unit")
    
    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'model', 'capacity', 'capacity_unit', 'capacity_display', 'active']
    
    def validate_capacity(self, value):
        """Validate capacity is reasonable"""
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0")
        if value > 50000:  # 50,000 kg or lb seems like a reasonable max
            raise serializers.ValidationError("Capacity seems unreasonably high")
        return value


class DriverVehicleSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    vehicle_license_plate = serializers.CharField(source='vehicle.license_plate', read_only=True)
    
    class Meta:
        model = DriverVehicle
        fields = ['id', 'driver', 'driver_name', 'vehicle', 'vehicle_license_plate', 'assigned_from', 'assigned_to']


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    vehicle_license_plate = serializers.CharField(source='vehicle.license_plate', read_only=True)
    customer_name = serializers.CharField(source='delivery.customer.display_name', read_only=True)
    
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'delivery', 'customer_name', 'driver', 'driver_name', 'vehicle', 'vehicle_license_plate', 'assigned_at']


class DriverWithVehicleSerializer(serializers.ModelSerializer):
    """Specialized serializer for creating driver with immediate vehicle assignment"""
    vehicle_id = serializers.IntegerField(required=True, help_text="ID of vehicle to assign to this driver")
    assigned_from = serializers.DateField(required=False, help_text="Date when vehicle assignment starts (defaults to today)")
    
    class Meta:
        model = Driver
        fields = ['name', 'phone_number', 'license_number', 'active', 'vehicle_id', 'assigned_from']
    
    def validate_vehicle_id(self, value):
        """Validate that the vehicle exists and is active"""
        try:
            vehicle = Vehicle.objects.get(id=value)
            if not vehicle.active:
                raise serializers.ValidationError("Selected vehicle is not active")
            return value
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError("Vehicle with this ID does not exist")
    
    def create(self, validated_data):
        from django.utils import timezone
        
        vehicle_id = validated_data.pop('vehicle_id')
        assigned_from = validated_data.pop('assigned_from', timezone.now().date())
        
        # Create driver
        driver = Driver.objects.create(**validated_data)
        
        # Assign vehicle
        vehicle = Vehicle.objects.get(id=vehicle_id)
        DriverVehicle.objects.create(
            driver=driver,
            vehicle=vehicle,
            assigned_from=assigned_from
        )
        
        return driver


class DriverRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for driver self-registration with User account creation"""
    username = serializers.CharField(source='user.username', help_text="Username for login")
    email = serializers.EmailField(source='user.email', help_text="Email address")
    password = serializers.CharField(source='user.password', write_only=True, min_length=8, help_text="Password for login")
    first_name = serializers.CharField(source='user.first_name', required=True, help_text="Driver's first name")
    last_name = serializers.CharField(source='user.last_name', required=True, help_text="Driver's last name")
    
    vehicle_license_plate = serializers.CharField(write_only=True, help_text="Vehicle license plate")
    vehicle_model = serializers.CharField(write_only=True, help_text="Vehicle model")
    vehicle_capacity = serializers.IntegerField(write_only=True, help_text="Vehicle capacity")
    vehicle_capacity_unit = serializers.ChoiceField(
        choices=Vehicle.CAPACITY_UNIT_CHOICES, 
        write_only=True, 
        default='kg',
        help_text="Capacity unit (kg or lb)"
    )
    
    class Meta:
        model = Driver
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                 'name', 'phone_number', 'license_number', 'vehicle_license_plate', 
                 'vehicle_model', 'vehicle_capacity', 'vehicle_capacity_unit']
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def validate_license_number(self, value):
        """Ensure license number is unique"""
        if Driver.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("This license number is already registered")
        return value
    
    def validate_vehicle_license_plate(self, value):
        """Ensure vehicle license plate is unique"""
        if Vehicle.objects.filter(license_plate=value).exists():
            raise serializers.ValidationError("This vehicle license plate is already registered")
        return value
    
    def create(self, validated_data):
        from django.utils import timezone
        
        # Extract user and vehicle data
        user_data = validated_data.pop('user')
        vehicle_data = {
            'license_plate': validated_data.pop('vehicle_license_plate'),
            'model': validated_data.pop('vehicle_model'),
            'capacity': validated_data.pop('vehicle_capacity'),
            'capacity_unit': validated_data.pop('vehicle_capacity_unit'),
            'active': True
        }
        
        # Create User
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        # Create driver with user link
        validated_data['name'] = f"{user_data['first_name']} {user_data['last_name']}"
        driver = Driver.objects.create(user=user, **validated_data, active=True)
        
        # Create vehicle
        vehicle = Vehicle.objects.create(**vehicle_data)
        
        # Create driver-vehicle assignment
        DriverVehicle.objects.create(
            driver=driver,
            vehicle=vehicle,
            assigned_from=timezone.now().date()
        )
        
        return driver