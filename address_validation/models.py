"""
Address Validation Models
Handles address validation and normalization
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ValidatedAddress(models.Model):
    """Store validated and normalized addresses"""
    
    VALIDATION_STATUS_CHOICES = [
        ('pending', 'Pending Validation'),
        ('valid', 'Valid Address'),
        ('invalid', 'Invalid Address'),
        ('partial', 'Partially Valid'),
    ]
    
    VALIDATION_SOURCE_CHOICES = [
        ('google', 'Google Maps API'),
        ('canada_post', 'Canada Post API'),
        ('manual', 'Manual Entry'),
        ('usaddress', 'US Address Parser'),
    ]
    
    # Original input
    original_address = models.TextField(help_text="Original address as entered by user")
    
    # Parsed components
    unit = models.CharField(max_length=50, blank=True, null=True, help_text="Unit/Apartment number")
    street_number = models.CharField(max_length=20, blank=True, null=True, help_text="Street number")
    street_name = models.CharField(max_length=255, blank=True, null=True, help_text="Street name")
    street_type = models.CharField(max_length=50, blank=True, null=True, help_text="Street type (St, Ave, Rd, etc.)")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="City name")
    state_province = models.CharField(max_length=50, blank=True, null=True, help_text="State or Province")
    postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Postal or ZIP code")
    country = models.CharField(max_length=50, blank=True, null=True, help_text="Country")
    
    # Normalized full address
    normalized_address = models.TextField(blank=True, null=True, help_text="Normalized full address")
    
    # Validation metadata
    validation_status = models.CharField(
        max_length=20, 
        choices=VALIDATION_STATUS_CHOICES, 
        default='pending'
    )
    validation_source = models.CharField(
        max_length=20, 
        choices=VALIDATION_SOURCE_CHOICES, 
        default='manual'
    )
    confidence_score = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Validation confidence score (0.0 - 1.0)"
    )
    
    # Geographic coordinates (if available)
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude coordinate")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who validated this address"
    )
    
    def __str__(self):
        return f"{self.normalized_address or self.original_address} ({self.validation_status})"
    
    @property
    def formatted_address(self):
        """Return formatted address string"""
        parts = []
        if self.unit:
            parts.append(f"Unit {self.unit}")
        if self.street_number and self.street_name:
            street = f"{self.street_number} {self.street_name}"
            if self.street_type:
                street += f" {self.street_type}"
            parts.append(street)
        if self.city:
            parts.append(self.city)
        if self.state_province:
            parts.append(self.state_province)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        
        return ", ".join(parts) if parts else self.original_address
    
    @property
    def is_valid(self):
        """Check if address is considered valid"""
        return self.validation_status == 'valid'
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['validation_status']),
            models.Index(fields=['postal_code']),
            models.Index(fields=['city', 'state_province']),
        ]


class AddressValidationLog(models.Model):
    """Log address validation attempts and API calls"""
    
    address = models.ForeignKey(ValidatedAddress, on_delete=models.CASCADE, related_name='validation_logs')
    validation_source = models.CharField(max_length=20, choices=ValidatedAddress.VALIDATION_SOURCE_CHOICES)
    request_data = models.JSONField(help_text="API request data")
    response_data = models.JSONField(help_text="API response data")
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.validation_source} validation - {status} ({self.created_at})"
    
    class Meta:
        ordering = ['-created_at']
