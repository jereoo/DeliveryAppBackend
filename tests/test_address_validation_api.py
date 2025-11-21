"""
Additional comprehensive tests for Address Validation API endpoints
Testing views, serializers, and service error conditions
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, Mock
from address_validation.models import ValidatedAddress, AddressValidationLog
from address_validation.serializers import (
    ValidatedAddressSerializer, 
    AddressValidationLogSerializer,
    AddressValidationRequestSerializer
)
from address_validation.services import AddressValidationService


class AddressValidationSerializerTests(TestCase):
    """Test address validation serializers"""
    
    def test_validated_address_serializer(self):
        """Test ValidatedAddress serialization"""
        address = ValidatedAddress.objects.create(
            original_address='123 Test St',
            street_number='123',
            street_name='Test',
            street_type='St',
            validation_status='valid',
            confidence_score=0.9
        )
        
        serializer = ValidatedAddressSerializer(address)
        data = serializer.data
        
        self.assertEqual(data['original_address'], '123 Test St')
        self.assertEqual(data['validation_status'], 'valid')
        self.assertEqual(data['confidence_score'], 0.9)
        self.assertIn('formatted_address', data)
        self.assertIn('is_valid', data)
    
    def test_address_validation_request_serializer(self):
        """Test address validation request serializer"""
        data = {
            'address': '123 Main St',
            'country_hint': 'US'
        }
        
        serializer = AddressValidationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['address'], '123 Main St')
        self.assertEqual(serializer.validated_data['country_hint'], 'US')
    
    def test_address_validation_request_invalid(self):
        """Test invalid address validation request"""
        data = {
            'country_hint': 'INVALID'
        }
        
        serializer = AddressValidationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('address', serializer.errors)
        self.assertIn('country_hint', serializer.errors)


class AddressValidationAPITests(APITestCase):
    """Test address validation API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_validate_endpoint_requires_auth(self):
        """Test that validation endpoint requires authentication"""
        client = APIClient()  # No auth
        url = '/api/address-validation/validate/'
        data = {'address': '123 Test St'}
        
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('address_validation.views.validate_address')
    def test_validate_endpoint_success(self, mock_validate):
        """Test successful address validation endpoint"""
        # Mock the validation service
        mock_address = ValidatedAddress.objects.create(
            original_address='123 Test St',
            validation_status='valid',
            confidence_score=0.9
        )
        mock_validate.return_value = mock_address
        
        url = '/api/address-validation/validate/'
        data = {
            'address': '123 Test St',
            'country_hint': 'US'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['original_address'], '123 Test St')
        self.assertEqual(response.data['validation_status'], 'valid')
        
        # Verify service was called with correct parameters
        mock_validate.assert_called_once_with('123 Test St', 'US')
    
    def test_validate_endpoint_missing_address(self):
        """Test validation endpoint with missing address"""
        url = '/api/address-validation/validate/'
        data = {'country_hint': 'US'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('address', response.data)
        self.assertEqual(response.data['address'][0], 'This field is required.')
    
    @patch('address_validation.views.validate_address')
    def test_validate_endpoint_service_error(self, mock_validate):
        """Test validation endpoint with service error"""
        mock_validate.side_effect = Exception('Service error')
        
        url = '/api/address-validation/validate/'
        data = {'address': '123 Test St'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertIn('Validation failed', response.data['error'])
    
    @patch('address_validation.views.get_validation_statistics')
    def test_statistics_endpoint(self, mock_get_stats):
        """Test statistics endpoint"""
        mock_get_stats.return_value = {
            'total': 100,
            'valid': 80,
            'invalid': 10,
            'partial': 5,
            'pending': 5,
            'success_rate': 85.0
        }
        
        url = '/api/address-validation/statistics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 100)
        self.assertEqual(response.data['success_rate'], 85.0)


class AddressValidationServiceErrorTests(TestCase):
    """Test error handling in address validation service"""
    
    def setUp(self):
        self.service = AddressValidationService()
    
    @patch.object(AddressValidationService, '_parse_us_address')
    def test_validate_us_address_with_usaddress_error(self, mock_parse):
        """Test US address validation with usaddress parsing error"""
        mock_parse.side_effect = Exception('Parsing failed')
        
        address = ValidatedAddress.objects.create(
            original_address='Invalid Address',
            validation_status='pending'
        )
        
        # Should raise exception but create error log
        with self.assertRaises(Exception):
            self.service._validate_us_address(address)
        
        # Verify error log was created
        log = AddressValidationLog.objects.filter(address=address).first()
        self.assertIsNotNone(log)
        self.assertFalse(log.success)
        self.assertEqual(log.error_message, 'Parsing failed')
        self.assertGreater(log.processing_time, 0)
    
    def test_validate_canadian_address_basic(self):
        """Test Canadian address validation basic functionality"""
        address = ValidatedAddress.objects.create(
            original_address='123 Maple St, Toronto, ON M5V 3A8',
            validation_status='pending'
        )
        
        with patch('address_validation.services.usaddress.tag') as mock_tag:
            mock_tag.return_value = (
                {
                    'AddressNumber': '123',
                    'StreetName': 'Maple',
                    'StreetNamePostType': 'St'
                },
                'Street Address'
            )
            
            self.service._validate_canadian_address(address)
        
        address.refresh_from_db()
        self.assertEqual(address.validation_status, 'partial')
        self.assertEqual(address.validation_source, 'manual')
        self.assertEqual(address.country, 'Canada')
        self.assertEqual(address.confidence_score, 0.5)
        
        # Verify log was created
        log = AddressValidationLog.objects.filter(address=address).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.success)
        self.assertEqual(log.validation_source, 'canada_post')
    
    def test_update_address_components_with_empty_data(self):
        """Test updating address components with empty parsed data"""
        address = ValidatedAddress.objects.create(
            original_address='Test Address',
            validation_status='pending'
        )
        
        # Should not crash with empty data
        self.service._update_address_components(address, {})
        
        # Address should remain unchanged
        self.assertEqual(address.street_number, None)
        self.assertEqual(address.street_name, None)
    
    def test_update_address_components_with_partial_data(self):
        """Test updating address components with partial data"""
        address = ValidatedAddress.objects.create(
            original_address='Test Address',
            validation_status='pending'
        )
        
        parsed_data = {
            'street_number': '456',
            'city': 'Test City'
            # Missing other fields
        }
        
        self.service._update_address_components(address, parsed_data)
        
        self.assertEqual(address.street_number, '456')
        self.assertEqual(address.city, 'Test City')
        self.assertEqual(address.street_name, '')  # Should be empty string
        self.assertEqual(address.state_province, '')  # Should be empty string


class AddressValidationModelPropertyTests(TestCase):
    """Test model properties and edge cases"""
    
    def test_formatted_address_with_minimal_data(self):
        """Test formatted address with minimal data"""
        address = ValidatedAddress.objects.create(
            original_address='Minimal Address',
            city='Test City'
        )
        
        self.assertEqual(address.formatted_address, 'Test City')
    
    def test_formatted_address_with_no_components(self):
        """Test formatted address with no parsed components"""
        address = ValidatedAddress.objects.create(
            original_address='Original Address Only'
        )
        
        self.assertEqual(address.formatted_address, 'Original Address Only')
    
    def test_validation_log_string_representation_failed(self):
        """Test validation log string representation for failed validation"""
        address = ValidatedAddress.objects.create(
            original_address='Test Address'
        )
        
        log = AddressValidationLog.objects.create(
            address=address,
            validation_source='google',
            request_data={},
            response_data={},
            success=False,
            processing_time=0.1
        )
        
        self.assertIn('google validation - FAILED', str(log))


class AddressValidationStatisticsTests(TestCase):
    """Test validation statistics functionality"""
    
    def test_statistics_with_zero_addresses(self):
        """Test statistics with no addresses in database"""
        from address_validation.services import get_validation_statistics
        
        stats = get_validation_statistics()
        
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['valid'], 0)
        self.assertEqual(stats['invalid'], 0)
        self.assertEqual(stats['partial'], 0)
        self.assertEqual(stats['pending'], 0)
        self.assertEqual(stats['valid_percentage'], 0)
        self.assertEqual(stats['success_rate'], 0)
    
    def test_statistics_calculations(self):
        """Test statistics percentage calculations"""
        from address_validation.services import get_validation_statistics
        
        # Create test data: 10 total addresses
        # 6 valid, 2 invalid, 1 partial, 1 pending
        for i in range(6):
            ValidatedAddress.objects.create(
                original_address=f'Valid Address {i}',
                validation_status='valid'
            )
        
        for i in range(2):
            ValidatedAddress.objects.create(
                original_address=f'Invalid Address {i}',
                validation_status='invalid'
            )
        
        ValidatedAddress.objects.create(
            original_address='Partial Address',
            validation_status='partial'
        )
        
        ValidatedAddress.objects.create(
            original_address='Pending Address',
            validation_status='pending'
        )
        
        stats = get_validation_statistics()
        
        self.assertEqual(stats['total'], 10)
        self.assertEqual(stats['valid'], 6)
        self.assertEqual(stats['invalid'], 2)
        self.assertEqual(stats['partial'], 1)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['valid_percentage'], 60.0)  # 6/10 * 100
        self.assertEqual(stats['success_rate'], 70.0)  # (6+1)/10 * 100