# delivery/serializers.py
from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User
from .models import (
    Delivery,
    Driver,
    Vehicle,
    DriverVehicle,
    DeliveryAssignment,
    Customer,
    LegalDocument,
    DriverApprovalStatus,
    VehicleApprovalStatus,
    VehicleManufacturer,
    VehicleModelSpec,
)
from .compliance_constants import DocumentType
from .vehicle_constants import (
    MAX_VEHICLE_CAPACITY_KG,
    MAX_VEHICLE_CAPACITY_LB,
    max_vehicle_capacity_for_unit,
)
from .registration_messages import (
    EMAIL_TAKEN,
    LICENSE_NUMBER_TAKEN,
    LICENSE_PLATE_TAKEN,
    USERNAME_TAKEN,
    VIN_TAKEN,
)
from .driver_license_validation import list_license_regions, validate_driver_license_number
from .vehicle_catalog_validation import (
    get_active_model_spec,
    max_capacity_for_spec,
    validate_capacity_for_spec,
    validate_model_year_for_spec,
)

class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True, min_length=8)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    display_name = serializers.CharField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'full_name', 'display_name', 
                 'phone_number', 'address', 'address_unit', 'address_street', 'address_city', 
                 'address_state', 'address_postal_code', 'address_country', 'full_address', 'company_name', 'is_business', 
                 'preferred_pickup_address', 'created_at', 'active']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def validate_phone_number(self, value):
        """North America: 10 digits only (area code 1 assumed)."""
        import re
        digits = re.sub(r'\D', '', value or '')
        if len(digits) != 10:
            raise serializers.ValidationError('Phone must be exactly 10 digits (North America, no area code).')
        return digits
    
    def create(self, validated_data):
        from .registration_service import create_customer_as_staff

        return create_customer_as_staff(validated_data)

    def update(self, instance, validated_data):
        # Extract user data
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
        # Update User fields if provided
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        # Update Customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True, min_length=8)
    first_name = serializers.CharField(source='user.first_name', required=True, help_text="Customer's first name")
    last_name = serializers.CharField(source='user.last_name', required=True, help_text="Customer's last name")
    
    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                 'phone_number', 'address_unit', 'address_street', 'address_city', 
                 'address_state', 'address_postal_code', 'address_country', 'company_name', 'is_business', 'preferred_pickup_address']
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(USERNAME_TAKEN)
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(EMAIL_TAKEN)
        return value

    def validate_phone_number(self, value):
        """North America: 10 digits only (area code 1 assumed)."""
        import re
        digits = re.sub(r'\D', '', value or '')
        if len(digits) != 10:
            raise serializers.ValidationError('Phone must be exactly 10 digits (North America, no area code).')
        return digits
    
    def validate(self, data):
        """Custom validation for postal code based on country"""
        import re
        
        postal_code = data.get('address_postal_code')
        country = data.get('address_country')
        
        if postal_code and country:
            postal_code = postal_code.strip().upper()
            
            if country == 'CA' or country == 'Canada':
                # Canadian postal code format: A1A 1A1 or A1A1A1
                # More flexible pattern to handle both formats
                canadian_pattern = r'^[A-Z]\d[A-Z]\s*\d[A-Z]\d$'
                if not re.match(canadian_pattern, postal_code):
                    raise serializers.ValidationError({
                        'address_postal_code': 'Canadian postal codes must be in the format A1A 1A1 or A1A1A1 (e.g., K1A 0A6)'
                    })
            elif country == 'US' or country == 'USA' or country == 'United States':
                # US ZIP code format: 12345 or 12345-1234
                us_pattern = r'^\d{5}(-\d{4})?$'
                if not re.match(us_pattern, postal_code):
                    raise serializers.ValidationError({
                        'address_postal_code': 'US ZIP codes must be in the format 12345 or 12345-1234'
                    })
            # Note: For other countries, we'll be more lenient and allow any format
        
        return data
    
    def create(self, validated_data):
        from .registration_service import register_customer

        return register_customer(validated_data)


class CustomerMeSerializer(serializers.ModelSerializer):
    """Self-service customer profile (no username/active changes)."""

    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    full_name = serializers.SerializerMethodField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number',
            'address_unit', 'address_street', 'address_city', 'address_state',
            'address_postal_code', 'address_country', 'full_address',
            'company_name', 'is_business', 'preferred_pickup_address', 'password',
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def validate_phone_number(self, value):
        import re
        digits = re.sub(r'\D', '', value or '')
        if len(digits) != 10:
            raise serializers.ValidationError(
                'Phone must be exactly 10 digits (North America, no area code).'
            )
        return digits

    def validate(self, data):
        import re

        postal_code = data.get('address_postal_code')
        country = data.get('address_country')
        if postal_code and country:
            postal_code = postal_code.strip().upper()
            if country == 'CA':
                canadian_pattern = r'^[A-Z]\d[A-Z]\s*\d[A-Z]\d$'
                if not re.match(canadian_pattern, postal_code):
                    raise serializers.ValidationError({
                        'address_postal_code': 'Canadian postal codes must be in the format A1A 1A1 or A1A1A1 (e.g., K1A 0A6)'
                    })
            elif country == 'US':
                us_pattern = r'^\d{5}(-\d{4})?$'
                if not re.match(us_pattern, postal_code):
                    raise serializers.ValidationError({
                        'address_postal_code': 'US ZIP codes must be in the format 12345 or 12345-1234'
                    })
        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password = validated_data.pop('password', None)
        user = instance.user
        if user_data or password:
            if 'email' in user_data:
                user.email = user_data['email']
            if 'first_name' in user_data:
                user.first_name = user_data['first_name']
            if 'last_name' in user_data:
                user.last_name = user_data['last_name']
            if password:
                user.set_password(password)
            user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


def _validate_delivery_location_fields(data, instance=None):
    """Shared pickup/dropoff rules for customer requests and admin CRUD."""
    errors = {}

    same_pickup = data.get('same_pickup_as_customer')
    if same_pickup is None and instance is not None:
        same_pickup = instance.same_pickup_as_customer
    use_preferred = data.get('use_preferred_pickup')
    if use_preferred is None and instance is not None:
        use_preferred = instance.use_preferred_pickup
    same_dropoff = data.get('same_dropoff_as_customer')
    if same_dropoff is None and instance is not None:
        same_dropoff = instance.same_dropoff_as_customer

    pickup_location = data.get('pickup_location')
    if pickup_location is None and instance is not None:
        pickup_location = instance.pickup_location
    dropoff_location = data.get('dropoff_location')
    if dropoff_location is None and instance is not None:
        dropoff_location = instance.dropoff_location

    if not same_pickup and not use_preferred and not pickup_location:
        errors['pickup_location'] = 'This field is required when not using customer address as pickup location.'
    if not same_dropoff and not dropoff_location:
        errors['dropoff_location'] = 'This field is required when not using customer address as dropoff location.'

    if errors:
        raise serializers.ValidationError(errors)
    return data


class DeliverySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.display_name', read_only=True)
    customer_email = serializers.EmailField(source='customer.user.email', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    pickup_location = serializers.CharField(required=False, allow_blank=True)
    dropoff_location = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Delivery
        fields = ['id', 'customer', 'customer_name', 'customer_email', 'customer_phone',
                 'pickup_location', 'dropoff_location', 'same_pickup_as_customer', 'use_preferred_pickup', 'same_dropoff_as_customer',
                 'item_description', 'status', 'delivery_date', 'delivery_time', 'special_instructions',
                 'estimated_cost', 'created_at', 'updated_at']

    def validate(self, data):
        if self.instance is None and not data.get('customer'):
            raise serializers.ValidationError({'customer': 'This field is required.'})
        return _validate_delivery_location_fields(data, self.instance)


class DeliveryCreateSerializer(serializers.ModelSerializer):
    """Serializer for customer creating their own delivery"""
    pickup_location = serializers.CharField(required=False, allow_blank=True, help_text="Pickup address (auto-filled if same_pickup_as_customer is True)")
    dropoff_location = serializers.CharField(required=False, allow_blank=True, help_text="Dropoff address (auto-filled if same_dropoff_as_customer is True)")
    
    class Meta:
        model = Delivery
        fields = ['pickup_location', 'dropoff_location', 'same_pickup_as_customer', 'use_preferred_pickup', 'same_dropoff_as_customer',
                 'item_description', 'delivery_date', 'delivery_time', 'special_instructions']
    
    def validate(self, data):
        return _validate_delivery_location_fields(data, self.instance)
    
    def create(self, validated_data):
        # Auto-assign customer from request user
        customer = self.context['request'].user.customer_profile
        validated_data['customer'] = customer
        return super().create(validated_data)


class DriverSerializer(serializers.ModelSerializer):
    # CIO DIRECTIVE: Direct access to User model fields via Driver model fields
    # No longer using SerializerMethodField - all drivers now have User accounts
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # Never change user on update
    # Optional vehicle assignment fields
    vehicle_id = serializers.IntegerField(write_only=True, required=False, help_text="ID of vehicle to assign to this driver")
    assigned_from = serializers.DateField(write_only=True, required=False, help_text="Date when vehicle assignment starts (defaults to today)")
    
    # Read-only fields to show current vehicle assignment
    current_vehicle = serializers.SerializerMethodField(read_only=True)
    current_vehicle_plate = serializers.SerializerMethodField(read_only=True)
    current_vehicle_model = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Driver
        fields = [
            'id', 'user', 'first_name', 'last_name', 'phone_number', 'license_number',
            'license_issuing_region',
            'address_unit', 'address_street', 'address_city', 'address_state',
            'address_postal_code', 'address_country',
            'active',
            'approval_status', 'approval_rejection_reason', 'approved_at',
            'vehicle_id', 'assigned_from', 'current_vehicle', 'current_vehicle_plate', 'current_vehicle_model',
        ]
        read_only_fields = ['approval_status', 'approval_rejection_reason', 'approved_at']
        # CIO DIRECTIVE: Removed deprecated 'name' field - use first_name + last_name from User model
    
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
    
    def get_current_vehicle_model(self, obj):
        """Get the currently assigned vehicle model"""
        from django.utils import timezone
        today = timezone.now().date()
        current_assignment = DriverVehicle.objects.filter(
            driver=obj,
            assigned_from__lte=today
        ).filter(
            models.Q(assigned_to__isnull=True) | models.Q(assigned_to__gte=today)
        ).order_by('-assigned_from').first()
        
        return current_assignment.vehicle.model if current_assignment and current_assignment.vehicle else None
    
    # CIO DIRECTIVE: Removed get_first_name/get_last_name methods
    # Direct field access to driver.first_name and driver.last_name now available

    def validate_phone_number(self, value):
        """North America: 10 digits only (area code 1 assumed). Format: 5555555555"""
        import re
        digits = re.sub(r'\D', '', value or '')
        if len(digits) != 10:
            raise serializers.ValidationError('Phone must be exactly 10 digits (North America, no area code).')
        return digits
    
    def create(self, validated_data):
        from django.utils import timezone
        from django.contrib.auth.models import User
        
        # Extract vehicle assignment data
        vehicle_id = validated_data.pop('vehicle_id', None)
        assigned_from = validated_data.pop('assigned_from', timezone.now().date())
        
        # CIO DIRECTIVE: Every driver must have a User account
        # Extract user data from validated_data
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        
        # Validate user exists (this is just extra safety - DRF foreign key validation should handle this)
        user = validated_data.get('user')
        if not user:
            raise serializers.ValidationError('Driver must be linked to a User account. Create User first or use DriverRegistrationSerializer.')
        
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
        
        # CIO DIRECTIVE: Handle User model field updates
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        
        # Update User model fields (every driver now has a user account)
        if first_name is not None or last_name is not None:
            if not instance.user:
                raise serializers.ValidationError('Driver has no User account. This violates CIO directive - all drivers must have users.')
            
            if first_name is not None:
                instance.user.first_name = first_name
                instance.first_name = first_name  # Update driver field too
            if last_name is not None:
                instance.user.last_name = last_name
                instance.last_name = last_name  # Update driver field too
            instance.user.save()
        
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


class StaffDriverCreateSerializer(serializers.ModelSerializer):
    """Admin creates a driver with linked User account (no vehicle bundled)."""

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    license_issuing_region = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Driver
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'license_number', 'license_issuing_region',
            'address_unit', 'address_street', 'address_city', 'address_state',
            'address_postal_code', 'address_country', 'active',
        ]

    def validate_phone_number(self, value):
        import re
        digits = re.sub(r'\D', '', value or '')
        if len(digits) != 10:
            raise serializers.ValidationError(
                'Phone must be exactly 10 digits (North America, no area code).'
            )
        return digits

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(USERNAME_TAKEN)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(EMAIL_TAKEN)
        return value

    def create(self, validated_data):
        from .registration_service import create_driver_as_staff

        return create_driver_as_staff(validated_data)


class VehicleSerializer(serializers.ModelSerializer):
    capacity_display = serializers.CharField(read_only=True, help_text="Formatted capacity with unit")
    full_model = serializers.CharField(read_only=True, help_text="Combined make and model for backward compatibility")
    model_spec_id = serializers.IntegerField(read_only=True, allow_null=True)
    identity_locked = serializers.SerializerMethodField()
    registration_verified = serializers.SerializerMethodField()
    can_replace_vehicle = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'license_plate', 'make', 'model', 'year', 'vin', 'capacity', 'capacity_unit',
            'capacity_display', 'full_model', 'active', 'approval_status', 'resubmit_reason',
            'approved_at', 'model_spec_id', 'identity_locked', 'registration_verified',
            'can_replace_vehicle',
        ]
        read_only_fields = ['approved_at']

    def get_identity_locked(self, obj: Vehicle) -> bool:
        from .vehicle_field_policy import identity_locked_for_driver
        return identity_locked_for_driver(obj)

    def get_registration_verified(self, obj: Vehicle) -> bool:
        from .vehicle_field_policy import vehicle_has_verified_registration
        return vehicle_has_verified_registration(obj)

    def get_can_replace_vehicle(self, obj: Vehicle) -> bool:
        from .vehicle_field_policy import driver_may_replace_vehicle
        return driver_may_replace_vehicle(obj)
    
    def validate(self, data):
        capacity = data.get('capacity')
        if capacity is None and self.instance:
            capacity = self.instance.capacity
        unit = data.get('capacity_unit')
        if unit is None and self.instance:
            unit = self.instance.capacity_unit
        if unit is None:
            unit = 'kg'
        if capacity is not None:
            if capacity <= 0:
                raise serializers.ValidationError({
                    'capacity': 'Capacity must be greater than 0',
                })
            max_cap = max_vehicle_capacity_for_unit(unit)
            if capacity > max_cap:
                raise serializers.ValidationError({
                    'capacity': (
                        f'Capacity cannot exceed {max_cap} {unit} '
                        f'(max {MAX_VEHICLE_CAPACITY_KG} kg / {MAX_VEHICLE_CAPACITY_LB} lb).'
                    ),
                })
        return data
    
    def validate_year(self, value):
        """Validate year is reasonable"""
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1900:
            raise serializers.ValidationError("Year must be 1900 or later")
        if value > current_year + 1:  # Allow next year for new models
            raise serializers.ValidationError(f"Year cannot be later than {current_year + 1}")
        return value
    
    def validate_vin(self, value):
        """Validate VIN format"""
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters")
        # Basic VIN validation - no I, O, Q characters
        invalid_chars = set('IOQ')
        if any(char in invalid_chars for char in value.upper()):
            raise serializers.ValidationError("VIN cannot contain I, O, or Q characters")
        return value.upper()


class DriverMeSerializer(serializers.ModelSerializer):
    """Self-service driver profile (no vehicle reassignment or active flag changes)."""

    active = serializers.BooleanField(read_only=True)
    approval_status = serializers.CharField(read_only=True)
    approval_rejection_reason = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta:
        model = Driver
        fields = [
            'id', 'first_name', 'last_name', 'phone_number', 'license_number',
            'license_issuing_region', 'active',
            'approval_status', 'approval_rejection_reason',
            'address_unit', 'address_street', 'address_city', 'address_state',
            'address_postal_code', 'address_country', 'full_address', 'password',
        ]

    def validate_phone_number(self, value):
        import re
        digits = re.sub(r'\D', '', value or '')
        if len(digits) != 10:
            raise serializers.ValidationError(
                'Phone must be exactly 10 digits (North America, no area code).'
            )
        return digits

    def validate_license_number(self, value):
        qs = Driver.objects.filter(license_number=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(LICENSE_NUMBER_TAKEN)
        return value

    def validate(self, data):
        import re

        postal_code = data.get('address_postal_code')
        country = data.get('address_country')
        if postal_code and country:
            postal_code = postal_code.strip().upper()
            if country == 'CA':
                canadian_pattern = r'^[A-Z]\d[A-Z]\s*\d[A-Z]\d$'
                if not re.match(canadian_pattern, postal_code):
                    raise serializers.ValidationError({
                        'address_postal_code': 'Canadian postal codes must be in the format A1A 1A1 or A1A1A1 (e.g., K1A 0A6)'
                    })
            elif country == 'US':
                us_pattern = r'^\d{5}(-\d{4})?$'
                if not re.match(us_pattern, postal_code):
                    raise serializers.ValidationError({
                        'address_postal_code': 'US ZIP codes must be in the format 12345 or 12345-1234'
                    })
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        user = instance.user
        if first_name is not None or last_name is not None or password:
            if first_name is not None:
                user.first_name = first_name
                instance.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
                instance.last_name = last_name
            if password:
                user.set_password(password)
            user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DriverOwnedVehicleSerializer(VehicleSerializer):
    """Vehicle fields a driver may edit on their currently assigned vehicle."""

    active = serializers.BooleanField(required=False)

    class Meta(VehicleSerializer.Meta):
        read_only_fields = [
            'id', 'capacity_display', 'full_model', 'approval_status', 'resubmit_reason',
            'approved_at', 'model_spec_id', 'identity_locked', 'registration_verified',
            'can_replace_vehicle',
        ]

    def validate_active(self, value):
        if self.instance and not self.instance.active and value is True:
            raise serializers.ValidationError('Only staff can reactivate a vehicle.')
        return value

    def update(self, instance, validated_data):
        mark_inactive = validated_data.get('active') is False and instance.active
        instance = super().update(instance, validated_data)
        if mark_inactive:
            from .vehicle_utils import deactivate_vehicle
            deactivate_vehicle(instance)
            instance.refresh_from_db()
        return instance

    def validate_license_plate(self, value):
        qs = Vehicle.objects.filter(license_plate=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(LICENSE_PLATE_TAKEN)
        return value

    def validate_vin(self, value):
        value = value.upper()
        qs = Vehicle.objects.filter(vin=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(VIN_TAKEN)
        return super().validate_vin(value)


class DriverVehicleSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField(read_only=True)
    vehicle_license_plate = serializers.CharField(source='vehicle.license_plate', read_only=True)
    
    def get_driver_name(self, obj):
        """Get driver full name from first_name + last_name"""
        if obj.driver:
            return f"{obj.driver.first_name} {obj.driver.last_name}".strip()
        return ""
    
    class Meta:
        model = DriverVehicle
        fields = ['id', 'driver', 'driver_name', 'vehicle', 'vehicle_license_plate', 'assigned_from', 'assigned_to']


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField(read_only=True)
    vehicle_license_plate = serializers.CharField(source='vehicle.license_plate', read_only=True)
    customer_name = serializers.CharField(source='delivery.customer.display_name', read_only=True)
    
    def get_driver_name(self, obj):
        """Get driver full name from first_name + last_name"""
        if obj.driver:
            return f"{obj.driver.first_name} {obj.driver.last_name}".strip()
        return ""

    def create(self, validated_data):
        from . import compliance_service

        compliance_service.assert_driver_eligible_for_dispatch(validated_data['driver'])
        return super().create(validated_data)
    
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'delivery', 'customer_name', 'driver', 'driver_name', 'vehicle', 'vehicle_license_plate', 'assigned_at']


class DriverWithVehicleSerializer(serializers.ModelSerializer):
    """Specialized serializer for creating driver with immediate vehicle assignment"""
    vehicle_id = serializers.IntegerField(required=True, help_text="ID of vehicle to assign to this driver")
    assigned_from = serializers.DateField(required=False, help_text="Date when vehicle assignment starts (defaults to today)")
    
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'phone_number', 'license_number', 'active', 'vehicle_id', 'assigned_from']
    
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
        vehicle = Vehicle.objects.get(id=vehicle_id)
        DriverVehicle.objects.create(
            driver=driver,
            vehicle=vehicle,
            assigned_from=assigned_from
        )
        
        return driver


class VehicleModelSpecCatalogSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    max_payload_kg = serializers.IntegerField(read_only=True)
    max_capacity_kg = serializers.SerializerMethodField()
    max_capacity_lb = serializers.SerializerMethodField()

    class Meta:
        model = VehicleModelSpec
        fields = [
            'id',
            'manufacturer_name',
            'name',
            'start_year',
            'end_year',
            'max_payload_lb',
            'max_payload_kg',
            'max_towing_lb',
            'max_capacity_kg',
            'max_capacity_lb',
            'notes',
        ]

    def get_max_capacity_kg(self, obj: VehicleModelSpec) -> int:
        return max_capacity_for_spec(obj, 'kg')

    def get_max_capacity_lb(self, obj: VehicleModelSpec) -> int:
        return max_capacity_for_spec(obj, 'lb')


class VehicleManufacturerCatalogSerializer(serializers.ModelSerializer):
    models = VehicleModelSpecCatalogSerializer(source='model_specs', many=True, read_only=True)

    class Meta:
        model = VehicleManufacturer
        fields = ['id', 'name', 'models']


class DriverRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for driver self-registration with User account creation"""
    username = serializers.CharField(source='user.username', help_text="Username for login")
    email = serializers.EmailField(source='user.email', help_text="Email address")
    password = serializers.CharField(source='user.password', write_only=True, min_length=8, help_text="Password for login")
    first_name = serializers.CharField(source='user.first_name', required=False, help_text="Driver's first name")
    last_name = serializers.CharField(source='user.last_name', required=False, help_text="Driver's last name")
    full_name = serializers.CharField(write_only=True, required=False, help_text="Full name (alternative to first_name + last_name)")
    
    vehicle_license_plate = serializers.CharField(write_only=True, help_text="Vehicle license plate")
    vehicle_model_spec_id = serializers.IntegerField(
        write_only=True,
        help_text='Catalog id for vehicle make/model (from GET /vehicle-catalog/)',
    )
    vehicle_year = serializers.IntegerField(write_only=True, help_text="Vehicle manufacturing year")
    vehicle_vin = serializers.CharField(write_only=True, max_length=17, help_text="Vehicle VIN")
    vehicle_capacity = serializers.IntegerField(write_only=True, help_text="Vehicle capacity")
    vehicle_capacity_unit = serializers.ChoiceField(
        choices=Vehicle.CAPACITY_UNIT_CHOICES, 
        write_only=True, 
        default='kg',
        help_text="Capacity unit (kg or lb)"
    )
    license_issuing_region = serializers.CharField(
        write_only=True,
        help_text='Province/state code, e.g. CA-BC or US-CA',
    )
    
    class Meta:
        model = Driver
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'full_name',
                 'phone_number', 'license_number', 'license_issuing_region',
                 'address_unit', 'address_street', 'address_city', 'address_state',
                 'address_postal_code', 'address_country',
                 'vehicle_license_plate', 'vehicle_model_spec_id', 'vehicle_year', 'vehicle_vin',
                 'vehicle_capacity', 'vehicle_capacity_unit']
        extra_kwargs = {
            'license_number': {'validators': []},
        }
    
    def validate(self, data):
        """Validate and process name fields"""
        # Extract user data for processing
        user_data = data.get('user', {})
        full_name = data.get('full_name')
        
        # If full_name is provided, split it into first_name and last_name
        if full_name:
            name_parts = full_name.strip().split()
            if len(name_parts) < 2:
                raise serializers.ValidationError({
                    'full_name': 'Please provide both first and last name (e.g., "John Smith")'
                })
            
            # Set first_name and last_name from full_name
            user_data['first_name'] = name_parts[0]
            user_data['last_name'] = ' '.join(name_parts[1:])  # Handle multiple last names
            data['user'] = user_data
        
        # Ensure we have either full_name or both first_name and last_name
        elif not (user_data.get('first_name') and user_data.get('last_name')):
            raise serializers.ValidationError({
                'name': 'Please provide either full_name or both first_name and last_name'
            })

        capacity = data.get('vehicle_capacity')
        unit = data.get('vehicle_capacity_unit', 'kg')
        spec_id = data.get('vehicle_model_spec_id')
        vehicle_year = data.get('vehicle_year')

        if spec_id is None:
            raise serializers.ValidationError({
                'vehicle_model_spec_id': 'Select a vehicle make and model from the catalog.',
            })

        from django.core.exceptions import ValidationError as DjangoValidationError

        try:
            spec = get_active_model_spec(spec_id)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc

        if vehicle_year is not None:
            try:
                validate_model_year_for_spec(spec, vehicle_year)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict) from exc

        if capacity is not None:
            try:
                validate_capacity_for_spec(spec, capacity, unit)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict) from exc

        data['_vehicle_model_spec'] = spec

        region = data.get('license_issuing_region')
        license_number = data.get('license_number')
        if not region:
            raise serializers.ValidationError({
                'license_issuing_region': 'Select the province or state that issued your driver license.',
            })

        try:
            normalized = validate_driver_license_number(region, license_number or '')
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        if Driver.objects.filter(license_number=normalized).exists():
            raise serializers.ValidationError({'license_number': LICENSE_NUMBER_TAKEN})
        data['license_number'] = normalized

        return data
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(USERNAME_TAKEN)
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(EMAIL_TAKEN)
        return value
    
    def validate_license_number(self, value):
        """Basic presence check; format/uniqueness handled in validate()."""
        if not (value or '').strip():
            raise serializers.ValidationError('Driver license number is required.')
        return value

    def validate_license_issuing_region(self, value):
        codes = {region['code'] for region in list_license_regions()}
        if value not in codes:
            raise serializers.ValidationError('Select a valid province or state.')
        return value
    
    def validate_vehicle_license_plate(self, value):
        """Ensure vehicle license plate is unique"""
        if Vehicle.objects.filter(license_plate=value).exists():
            raise serializers.ValidationError(LICENSE_PLATE_TAKEN)
        return value
    
    def validate_vehicle_vin(self, value):
        """Ensure vehicle VIN is unique and properly formatted"""
        if Vehicle.objects.filter(vin=value).exists():
            raise serializers.ValidationError(VIN_TAKEN)
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters")
        return value.upper()
    
    def create(self, validated_data):
        from .registration_service import register_driver

        return register_driver(validated_data)


class DriverReplaceVehicleSerializer(serializers.Serializer):
    vehicle_model_spec_id = serializers.IntegerField()
    vehicle_year = serializers.IntegerField()
    vehicle_license_plate = serializers.CharField(max_length=20)
    vehicle_vin = serializers.CharField(max_length=17)
    vehicle_capacity = serializers.IntegerField()
    vehicle_capacity_unit = serializers.ChoiceField(choices=Vehicle.CAPACITY_UNIT_CHOICES, default='lb')


class DriverVehicleResubmitSerializer(serializers.Serializer):
    vehicle_model_spec_id = serializers.IntegerField()
    vehicle_year = serializers.IntegerField()
    vehicle_license_plate = serializers.CharField(max_length=20)
    vehicle_vin = serializers.CharField(max_length=17)
    vehicle_capacity = serializers.IntegerField()
    vehicle_capacity_unit = serializers.ChoiceField(choices=Vehicle.CAPACITY_UNIT_CHOICES, default='lb')


class VehicleResubmitRequestSerializer(serializers.Serializer):
    resubmit_reason = serializers.CharField(max_length=2000)


class LegalDocumentSerializer(serializers.ModelSerializer):
    verified_by_username = serializers.CharField(source='verified_by.username', read_only=True)

    class Meta:
        model = LegalDocument
        fields = [
            'id', 'document_type', 'driver', 'vehicle', 'policy_number', 'issuer',
            'coverage_type', 'effective_date', 'expiry_date', 'file_key', 'file_name',
            'status', 'verified_by', 'verified_by_username', 'verified_at',
            'rejection_reason', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'status', 'verified_by', 'verified_by_username', 'verified_at',
            'rejection_reason', 'created_at', 'updated_at',
        ]


class LegalDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = [
            'document_type', 'policy_number', 'issuer', 'coverage_type',
            'effective_date', 'expiry_date', 'file_key', 'file_name', 'notes',
        ]

    def validate_document_type(self, value):
        if value not in DocumentType.values:
            raise serializers.ValidationError('Invalid document type.')
        return value


class LegalDocumentVerifySerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)


class LegalDocumentRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=True, allow_blank=False)


class DriverRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=True, allow_blank=False)


class PresignedUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=128)
    file_size = serializers.IntegerField(required=False, min_value=1)