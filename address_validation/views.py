"""
Address Validation API Views and Endpoints
RESTful API for address validation functionality
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ValidatedAddress, AddressValidationLog
from .services import validate_address, get_validation_statistics
from .serializers import (
    ValidatedAddressSerializer, 
    AddressValidationLogSerializer,
    AddressValidationRequestSerializer
)


class AddressValidationViewSet(viewsets.ModelViewSet):
    """ViewSet for address validation operations"""
    
    queryset = ValidatedAddress.objects.all()
    serializer_class = ValidatedAddressSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """
        Validate a single address
        
        POST /api/address-validation/validate/
        {
            "address": "123 Main St, Toronto, ON",
            "country_hint": "CA"
        }
        """
        address_text = request.data.get('address')
        country_hint = request.data.get('country_hint', 'US')
        
        if not address_text:
            return Response(
                {'error': 'Address is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validated_address = validate_address(address_text, country_hint)
            serializer = self.get_serializer(validated_address)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Validation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get address validation statistics
        
        GET /api/address-validation/statistics/
        """
        try:
            stats = get_validation_statistics()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Statistics failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidatedAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for validated addresses (read-only)"""
    
    queryset = ValidatedAddress.objects.all()
    serializer_class = ValidatedAddressSerializer
    permission_classes = [IsAuthenticated]


class AddressValidationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for validation logs (read-only)"""
    
    queryset = AddressValidationLog.objects.all()
    serializer_class = AddressValidationLogSerializer
    permission_classes = [IsAuthenticated]


class ValidateAddressView(APIView):
    """Standalone address validation endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Validate a single address"""
        serializer = AddressValidationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        address_text = serializer.validated_data['address']
        country_hint = serializer.validated_data.get('country_hint', 'US')
        
        if not address_text:
            return Response(
                {'error': 'Address is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validated_address = validate_address(address_text, country_hint)
            result_serializer = ValidatedAddressSerializer(validated_address)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Validation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidationStatisticsView(APIView):
    """Standalone validation statistics endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get address validation statistics"""
        try:
            stats = get_validation_statistics()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Statistics failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
