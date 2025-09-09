# delivery/admin.py
from django.contrib import admin
from django import forms
from .models import Delivery, Driver, Vehicle, DeliveryAssignment, DriverVehicle

# Custom form for admin, vehicle, driver, delivery assignment
class DeliveryAssignmentAdminForm(forms.ModelForm):
    class Meta:
        model = DeliveryAssignment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].disabled = True

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_address', 'pickup_location', 'dropoff_location', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_address', 'pickup_location', 'dropoff_location')
    
    readonly_fields = ('created_at',)  # Fixed: Added trailing comma
    
    fieldsets = (
        (None, {
            'fields': (
                'customer_name', 'customer_address', 'item_description', 
                'same_pickup_as_customer', 'pickup_location', 'dropoff_location',
                'status', 'delivery_date', 'delivery_time'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'license_number', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'license_number')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'model', 'capacity', 'active')
    list_filter = ('active',)
    search_fields = ('license_plate', 'model')

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    form = DeliveryAssignmentAdminForm
    list_display = ('delivery', 'driver', 'vehicle', 'assigned_at')
    list_filter = ('assigned_at',)
    search_fields = ('delivery__id', 'driver__name', 'vehicle__license_plate')  # Updated from delivery__order_id

@admin.register(DriverVehicle)
class DriverVehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'vehicle', 'assigned_from', 'assigned_to')
    list_filter = ('assigned_from', 'assigned_to')
    search_fields = ('driver__name', 'vehicle__license_plate')