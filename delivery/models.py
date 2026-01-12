from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

class Customer(models.Model):
    COUNTRY_CHOICES = [
        ('CA', 'Canada'),
        ('US', 'United States'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20)
    
    # Separate address fields
    address_unit = models.CharField(max_length=20, blank=True, null=True, help_text="Unit/Apartment number")
    address_street = models.CharField(max_length=255, blank=True, null=True, help_text="Street address")
    address_city = models.CharField(max_length=100, blank=True, null=True, help_text="City")
    address_state = models.CharField(max_length=100, blank=True, null=True, help_text="State/Province")
    address_postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Postal/ZIP code")
    address_country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='US', help_text="Country")
    
    # Legacy address field (for migration compatibility)
    address = models.TextField(blank=True, null=True, help_text="Legacy combined address field")
    
    company_name = models.CharField(max_length=255, blank=True, null=True, help_text="Optional company name")
    is_business = models.BooleanField(default=False, help_text="Is this a business customer?")
    preferred_pickup_address = models.TextField(blank=True, null=True, help_text="Default pickup address if different from main address")
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.is_business and self.company_name:
            return f"{self.company_name} ({self.user.email})"
        full_name = self.user.get_full_name()
        if full_name:
            return f"{full_name} ({self.user.email})"
        return f"{self.user.username} ({self.user.email})"

    @property
    def display_name(self):
        """Get display name for customer (company name or individual name)"""
        if self.is_business and self.company_name:
            return self.company_name
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username
    
    @property
    def full_address(self):
        """Combine separate address fields into a single formatted address"""
        address_parts = []
        if self.address_unit:
            address_parts.append(f"Unit {self.address_unit}")
        if self.address_street:
            address_parts.append(self.address_street)
        if self.address_city:
            address_parts.append(self.address_city)
        if self.address_state:
            address_parts.append(self.address_state)
        if self.address_postal_code:
            address_parts.append(self.address_postal_code)
        if self.address_country:
            country_name = dict(self.COUNTRY_CHOICES).get(self.address_country, self.address_country)
            address_parts.append(country_name)
        return ", ".join(address_parts) if address_parts else self.address or ""

    def validate_postal_code(self):
        """Validate postal code format based on country"""
        if not self.address_postal_code or not self.address_country:
            return  # Skip validation if postal code or country is not provided
            
        postal_code = self.address_postal_code.strip().upper()
        
        if self.address_country == 'CA':
            # Canadian postal code format: A1A 1A1
            canadian_pattern = r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$'
            if not re.match(canadian_pattern, postal_code):
                raise ValidationError({
                    'address_postal_code': 'Canadian postal codes must be in the format A1A 1A1 (e.g., K1A 0A6)'
                })
        elif self.address_country == 'US':
            # US ZIP code format: 12345 or 12345-1234
            us_pattern = r'^\d{5}(-\d{4})?$'
            if not re.match(us_pattern, postal_code):
                raise ValidationError({
                    'address_postal_code': 'US ZIP codes must be in the format 12345 or 12345-1234'
                })

    def clean(self):
        """Custom validation for the model"""
        super().clean()
        self.validate_postal_code()

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        # Only run validation if explicitly requested
        if kwargs.pop('validate', False):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('En Route', 'En Route'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='deliveries', null=True, blank=True)
    pickup_location = models.TextField()
    dropoff_location = models.TextField()
    same_pickup_as_customer = models.BooleanField(default=False, help_text="Use customer's main address as pickup location")
    use_preferred_pickup = models.BooleanField(default=False, help_text="Use customer's preferred pickup address")
    same_dropoff_as_customer = models.BooleanField(default=False, help_text="Use customer's main address as dropoff location")
    item_description = models.CharField(max_length=255, help_text="Describe the item to be picked up (e.g. TV, sofa, furniture)", default='Pending')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    special_instructions = models.TextField(blank=True, null=True, help_text="Special delivery instructions")
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Estimated delivery cost")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-set pickup location based on customer preferences
        if self.same_pickup_as_customer:
            self.pickup_location = self.customer.full_address
        elif self.use_preferred_pickup and self.customer.preferred_pickup_address:
            self.pickup_location = self.customer.preferred_pickup_address
            
        # Auto-set dropoff location based on customer preferences
        if self.same_dropoff_as_customer:
            self.dropoff_location = self.customer.full_address
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Delivery {self.id} for {self.customer.display_name}"
    
    @property
    def customer_name(self):
        """Backward compatibility property"""
        return self.customer.display_name

    class Meta:
        ordering = ['-created_at']

    
class Driver(models.Model):
    # CIO DIRECTIVE: Fixed OneToOneField relationship - PROTECT prevents cascade deletion
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='driver_profile')
    
    # NEW: Separate first_name, last_name fields (mirror auth_user)
    first_name = models.CharField(max_length=150, blank=True, help_text='Driver first name')
    last_name = models.CharField(max_length=150, blank=True, help_text='Driver last name')
    
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def clean(self):
        """CIO DIRECTIVE: Validate that every driver has a User account"""
        from django.core.exceptions import ValidationError
        if not self.user_id:
            raise ValidationError('Driver must be linked to a User account. NULL user_id not allowed.')
    
    def save(self, *args, **kwargs):
        """Override save to enforce validation"""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user and (self.user.first_name or self.user.last_name):
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return f"Driver #{self.id}"

    @property
    def full_name(self):
        """Get full name from User model"""
        if self.user and (self.user.first_name or self.user.last_name):
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return 'Unknown Driver'

    class Meta:
        ordering = ['-id']
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False),
                name='driver_must_have_user'
            )
        ]


class Vehicle(models.Model):
    CAPACITY_UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('lb', 'Pounds'),
    ]
    
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50, help_text="Vehicle manufacturer (e.g., Ford, Toyota)")
    model = models.CharField(max_length=50, help_text="Vehicle model (e.g., Transit, Hiace)")
    year = models.PositiveIntegerField(help_text="Manufacturing year")
    vin = models.CharField(max_length=17, unique=True, help_text="Vehicle Identification Number")
    capacity = models.PositiveIntegerField(help_text="Vehicle load capacity")
    capacity_unit = models.CharField(
        max_length=2, 
        choices=CAPACITY_UNIT_CHOICES, 
        default='kg',
        help_text="Unit of measurement for capacity"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year}) - {self.license_plate} - {self.capacity}{self.capacity_unit}"
    
    @property
    def capacity_display(self):
        """Return formatted capacity with unit"""
        return f"{self.capacity} {self.get_capacity_unit_display()}"

    @property
    def full_model(self):
        """Return combined make and model for backward compatibility"""
        return f"{self.make} {self.model}"

    class Meta:
        ordering = ['-id']


class DriverVehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_from = models.DateField()
    assigned_to = models.DateField(null=True, blank=True)  # null means currently assigned

    class Meta:
        unique_together = ('driver', 'vehicle', 'assigned_from')
        ordering = ['-assigned_from']

    def __str__(self):
        vehicle_info = self.vehicle.license_plate if self.vehicle else "No Vehicle"
        return f"{self.driver.full_name} -> {vehicle_info} (from {self.assigned_from})"




class DeliveryAssignment(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-assign vehicle from DriverVehicle if not manually provided
        if self.driver and not self.vehicle:
            today = timezone.now().date()
            driver_vehicle = DriverVehicle.objects.filter(
                driver=self.driver,
                assigned_from__lte=today
            ).filter(
                models.Q(assigned_to__isnull=True) | models.Q(assigned_to__gte=today)
            ).order_by('-assigned_from').first()

            if driver_vehicle and driver_vehicle.vehicle:
                self.vehicle = driver_vehicle.vehicle

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assignment for {self.delivery.id} to {self.driver}"

    class Meta:
        ordering = ['-assigned_at']
