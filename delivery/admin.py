# delivery/admin.py
from django.contrib import admin
from django import forms
from .models import Delivery, Driver, Vehicle, DeliveryAssignment, DriverVehicle, Customer

# Custom form for admin, vehicle, driver, delivery assignment
class DeliveryAssignmentAdminForm(forms.ModelForm):
    class Meta:
        model = DeliveryAssignment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].disabled = True

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_username', 'user_email', 'phone_number', 'is_business', 'active', 'created_at')
    list_filter = ('is_business', 'active', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'company_name', 'phone_number')
    readonly_fields = ('created_at',)
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_display_name', 'pickup_location', 'dropoff_location', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username', 'customer__user__email', 'customer__company_name', 
                    'pickup_location', 'dropoff_location', 'item_description')
    
    readonly_fields = ('created_at', 'updated_at')
    
    def customer_display_name(self, obj):
        return obj.customer.display_name
    customer_display_name.short_description = 'Customer'
    
    fieldsets = (
        (None, {
            'fields': (
                'customer', 'item_description', 'same_pickup_as_customer', 'use_preferred_pickup',
                'pickup_location', 'same_dropoff_as_customer', 'dropoff_location', 'status', 'delivery_date', 'delivery_time'
            )
        }),
        ('Additional Info', {
            'fields': ('special_instructions', 'estimated_cost'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    # CIO DIRECTIVE: Use User model fields instead of deprecated name field
    list_display = ('full_name_display', 'user_username', 'phone_number', 'license_number', 'active')
    list_filter = ('active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'license_number', 'phone_number')
    
    def full_name_display(self, obj):
        """Display driver's full name from User model"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return f"{obj.first_name} {obj.last_name}".strip() or f"Driver #{obj.id}"
    full_name_display.short_description = 'Full Name'
    
    def user_username(self, obj):
        """Display linked User username"""
        return obj.user.username if obj.user else 'No User Account'
    user_username.short_description = 'Username'
    
    # Remove deprecated name field from admin forms
    fields = ('user', 'first_name', 'last_name', 'phone_number', 'license_number', 'active')
    readonly_fields = ('first_name', 'last_name')  # These sync with User model
    
    def get_readonly_fields(self, request, obj=None):
        """Make first_name and last_name readonly - they sync with User model"""
        readonly = list(self.readonly_fields)
        if obj and obj.user:  # If editing existing driver with user
            readonly.extend(['first_name', 'last_name'])
        return readonly

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
    search_fields = ('delivery__id', 'driver__user__username', 'driver__user__first_name', 'driver__user__last_name', 'vehicle__license_plate')  # CIO DIRECTIVE: Use User fields

@admin.register(DriverVehicle)
class DriverVehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'vehicle', 'assigned_from', 'assigned_to')
    list_filter = ('assigned_from', 'assigned_to')
    search_fields = ('driver__user__username', 'driver__user__first_name', 'driver__user__last_name', 'vehicle__license_plate')  # CIO DIRECTIVE: Use User fields