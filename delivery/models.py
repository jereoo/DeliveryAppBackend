from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
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
            self.pickup_location = self.customer.address
        elif self.use_preferred_pickup and self.customer.preferred_pickup_address:
            self.pickup_location = self.customer.preferred_pickup_address
            
        # Auto-set dropoff location based on customer preferences
        if self.same_dropoff_as_customer:
            self.dropoff_location = self.customer.address
            
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class Vehicle(models.Model):
    CAPACITY_UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('lb', 'Pounds'),
    ]
    
    license_plate = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(help_text="Vehicle load capacity")
    capacity_unit = models.CharField(
        max_length=2, 
        choices=CAPACITY_UNIT_CHOICES, 
        default='kg',
        help_text="Unit of measurement for capacity"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.model} ({self.license_plate}) - {self.capacity}{self.capacity_unit}"
    
    @property
    def capacity_display(self):
        """Return formatted capacity with unit"""
        return f"{self.capacity} {self.get_capacity_unit_display()}"

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
        return f"{self.driver.name} -> {vehicle_info} (from {self.assigned_from})"




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
