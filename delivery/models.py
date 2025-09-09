from django.db import models
from django.utils import timezone

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('En Route', 'En Route'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=255)
    pickup_location = models.TextField()
    dropoff_location = models.TextField()
    customer_address = models.TextField()
    same_pickup_as_customer = models.BooleanField(default=False)
    item_description = models.CharField(max_length=255, help_text="Describe the item to be picked up (e.g. TV, sofa, furniture)", default='Pending')
    #status = models.CharField(max_length=50, default='Pending')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.same_pickup_as_customer:
            self.pickup_location = self.customer_address
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Delivery {self.id} for {self.customer_name}"

    
class Driver(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(help_text="Capacity in kg or number of items")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.model} ({self.license_plate})"


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
