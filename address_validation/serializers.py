"""
Address Validation Serializers
DRF serializers for address validation API
"""
from rest_framework import serializers
from .models import ValidatedAddress, AddressValidationLog


class ValidatedAddressSerializer(serializers.ModelSerializer):
    """Serializer for ValidatedAddress model"""
    
    formatted_address = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = ValidatedAddress
        fields = [
            'id',
            'original_address',
            'unit',
            'street_number',
            'street_name',
            'street_type',
            'city',
            'state_province',
            'postal_code',
            'country',
            'normalized_address',
            'formatted_address',
            'validation_status',
            'validation_source',
            'confidence_score',
            'latitude',
            'longitude',
            'is_valid',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'formatted_address',
            'is_valid',
            'created_at',
            'updated_at'
        ]


class AddressValidationLogSerializer(serializers.ModelSerializer):
    """Serializer for AddressValidationLog model"""
    
    class Meta:
        model = AddressValidationLog
        fields = [
            'id',
            'validation_source',
            'request_data',
            'response_data',
            'success',
            'error_message',
            'processing_time',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AddressValidationRequestSerializer(serializers.Serializer):
    """Serializer for address validation requests"""
    
    address = serializers.CharField(max_length=500, help_text="Address to validate")
    country_hint = serializers.ChoiceField(
        choices=[('US', 'United States'), ('CA', 'Canada')],
        default='US',
        help_text="Country hint for validation"
    )


class BatchAddressValidationRequestSerializer(serializers.Serializer):
    """Serializer for batch address validation requests"""
    
    addresses = serializers.ListField(
        child=AddressValidationRequestSerializer(),
        max_length=50,
        help_text="List of addresses to validate (max 50)"
    )