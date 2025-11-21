"""
Comprehensive tests for Address Validation System - API, Serializers, Services, Models
Required for RED status project - must achieve ≥80% coverage
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ValidatedAddress, AddressValidationLog
from .services import AddressValidationService, validate_address, get_validation_statistics
from .serializers import (
    ValidatedAddressSerializer, 
    AddressValidationLogSerializer,
    AddressValidationRequestSerializer
)


class ValidatedAddressModelTests(TestCase):
    """Test ValidatedAddress model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_validated_address(self):
        """Test creating a validated address"""
        address = ValidatedAddress.objects.create(
            original_address='123 Main St, Toronto, ON M5V 3A8',
            street_number='123',
            street_name='Main',
            street_type='St',
            city='Toronto',
            state_province='ON',
            postal_code='M5V 3A8',
            country='Canada',
            validation_status='valid',
            validation_source='google',
            confidence_score=0.95,
            latitude=43.6532,
            longitude=-79.3832,
            validated_by=self.user
        )
        
        self.assertEqual(address.original_address, '123 Main St, Toronto, ON M5V 3A8')
        self.assertEqual(address.validation_status, 'valid')
        self.assertEqual(address.validation_source, 'google')
        self.assertEqual(address.confidence_score, 0.95)
        self.assertTrue(address.is_valid)
    
    def test_formatted_address_property(self):
        """Test formatted address property"""
        address = ValidatedAddress.objects.create(
            original_address='456 Oak Ave, Unit 2B, New York, NY 10001',
            unit='2B',
            street_number='456',
            street_name='Oak',
            street_type='Ave',
            city='New York',
            state_province='NY',
            postal_code='10001',
            country='United States'
        )
        
        expected = 'Unit 2B, 456 Oak Ave, New York, NY, 10001, United States'
        self.assertEqual(address.formatted_address, expected)
    
    def test_is_valid_property(self):
        """Test is_valid property for different statuses"""
        # Valid address
        valid_address = ValidatedAddress.objects.create(
            original_address='Test Address',
            validation_status='valid'
        )
        self.assertTrue(valid_address.is_valid)
        
        # Invalid address
        invalid_address = ValidatedAddress.objects.create(
            original_address='Invalid Address',
            validation_status='invalid'
        )
        self.assertFalse(invalid_address.is_valid)


class AddressValidationLogModelTests(TestCase):
    """Test AddressValidationLog model functionality"""
    
    def setUp(self):
        self.address = ValidatedAddress.objects.create(
            original_address='123 Test St',
            validation_status='pending'
        )
    
    def test_create_validation_log(self):
        """Test creating a validation log"""
        log = AddressValidationLog.objects.create(
            address=self.address,
            validation_source='google',
            request_data={'address': '123 Test St'},
            response_data={'formatted_address': '123 Test Street'},
            success=True,
            processing_time=0.5
        )
        
        self.assertEqual(log.address, self.address)
        self.assertEqual(log.validation_source, 'google')
        self.assertTrue(log.success)
        self.assertEqual(log.processing_time, 0.5)


class AddressValidationServiceTests(TestCase):
    """Test AddressValidationService functionality"""
    
    def setUp(self):
        self.service = AddressValidationService()
    
    def test_service_initialization(self):
        """Test service initialization"""
        self.assertIsInstance(self.service, AddressValidationService)
        # Google client should be None without API key
        self.assertIsNone(self.service.google_client)
    
    @patch('address_validation.services.usaddress.tag')
    def test_parse_us_address(self, mock_usaddress_tag):
        """Test US address parsing"""
        mock_usaddress_tag.return_value = (
            {
                'AddressNumber': '123',
                'StreetName': 'Main',
                'StreetNamePostType': 'St',
                'PlaceName': 'Anytown',
                'StateName': 'NY',
                'ZipCode': '12345'
            },
            'Street Address'
        )
        
        result = self.service._parse_us_address('123 Main St, Anytown, NY 12345')
        
        self.assertEqual(result['street_number'], '123')
        self.assertEqual(result['street_name'], 'Main')
        self.assertEqual(result['street_type'], 'St')
        self.assertEqual(result['city'], 'Anytown')
        self.assertEqual(result['state'], 'NY')
        self.assertEqual(result['postal_code'], '12345')
    
    @patch('address_validation.services.usaddress.tag')
    def test_validate_us_address(self, mock_usaddress_tag):
        """Test US address validation"""
        mock_usaddress_tag.return_value = (
            {
                'AddressNumber': '789',
                'StreetName': 'Pine',
                'StreetNamePostType': 'Rd',
                'PlaceName': 'Test City',
                'StateName': 'CA',
                'ZipCode': '90210'
            },
            'Street Address'
        )
        
        address = ValidatedAddress.objects.create(
            original_address='789 Pine Rd, Test City, CA 90210',
            validation_status='pending'
        )
        
        self.service._validate_us_address(address)
        
        address.refresh_from_db()
        self.assertEqual(address.street_number, '789')
        self.assertEqual(address.street_name, 'Pine')
        self.assertEqual(address.validation_source, 'usaddress')
        self.assertEqual(address.validation_status, 'partial')
        self.assertEqual(address.confidence_score, 0.7)
    
    @patch('address_validation.services.usaddress.tag')
    def test_validate_address_convenience_function(self, mock_usaddress_tag):
        """Test the convenience validate_address function"""
        mock_usaddress_tag.return_value = (
            {
                'AddressNumber': '999',
                'StreetName': 'Test',
                'StreetNamePostType': 'Ave'
            },
            'Street Address'
        )
        
        result = validate_address('999 Test Ave', 'US')
        
        self.assertIsInstance(result, ValidatedAddress)
        self.assertEqual(result.original_address, '999 Test Ave')
        self.assertEqual(result.street_number, '999')
        self.assertEqual(result.street_name, 'Test')
    
    def test_get_validation_statistics_with_data(self):
        """Test validation statistics with sample data"""
        # Create sample addresses
        ValidatedAddress.objects.create(
            original_address='Valid Address 1',
            validation_status='valid'
        )
        ValidatedAddress.objects.create(
            original_address='Valid Address 2',
            validation_status='valid'
        )
        ValidatedAddress.objects.create(
            original_address='Invalid Address',
            validation_status='invalid'
        )
        
        stats = get_validation_statistics()
        
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['valid'], 2)
        self.assertEqual(stats['invalid'], 1)
    
    @patch('address_validation.services.usaddress.tag')
    def test_validate_us_address_with_usaddress_error(self, mock_tag):
        """Test US address validation with usaddress parsing error"""
        mock_tag.side_effect = Exception('Parsing failed')
        
        address = ValidatedAddress.objects.create(
            original_address='Invalid Address',
            validation_status='pending'
        )
        
        # Should not raise exception - usaddress errors are caught and logged
        self.service._validate_us_address(address)
        
        # Address should still be processed but with partial status
        address.refresh_from_db()
        self.assertEqual(address.validation_status, 'partial')
        self.assertEqual(address.validation_source, 'usaddress')
        
        # Verify success log was created (since parsing error is handled gracefully)
        log = AddressValidationLog.objects.filter(address=address).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.success)  # Success because error was handled gracefully
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
        self.assertIsNone(address.street_number)
        self.assertIsNone(address.street_name)
    
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
    
    def test_statistics_with_zero_addresses(self):
        """Test statistics with no addresses in database"""
        # Clear any existing addresses
        ValidatedAddress.objects.all().delete()
        
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
        # Clear existing and create test data: 10 total addresses
        ValidatedAddress.objects.all().delete()
        
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
    
    def test_address_validation_request_serializer_valid(self):
        """Test address validation request serializer with valid data"""
        data = {
            'address': '123 Main St',
            'country_hint': 'US'
        }
        
        serializer = AddressValidationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['address'], '123 Main St')
        self.assertEqual(serializer.validated_data['country_hint'], 'US')
    
    def test_address_validation_request_serializer_invalid_country(self):
        """Test invalid address validation request with bad country"""
        data = {
            'address': '123 Main St',
            'country_hint': 'INVALID'
        }
        
        serializer = AddressValidationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('country_hint', serializer.errors)
    
    def test_address_validation_request_serializer_missing_address(self):
        """Test address validation request missing required address"""
        data = {
            'country_hint': 'US'
        }
        
        serializer = AddressValidationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('address', serializer.errors)
    
    def test_address_validation_log_serializer(self):
        """Test AddressValidationLog serializer"""
        address = ValidatedAddress.objects.create(
            original_address='123 Test St'
        )
        
        log = AddressValidationLog.objects.create(
            address=address,
            validation_source='google',
            request_data={'address': '123 Test St'},
            response_data={'status': 'OK'},
            success=True,
            processing_time=0.5
        )
        
        serializer = AddressValidationLogSerializer(log)
        data = serializer.data
        
        self.assertEqual(data['validation_source'], 'google')
        self.assertTrue(data['success'])
        self.assertEqual(data['processing_time'], 0.5)


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
        # API returns serializer validation errors, not custom error message
        self.assertIn('address', response.data)
    
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
    def test_statistics_endpoint_success(self, mock_get_stats):
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
    
    def test_validated_addresses_list_endpoint(self):
        """Test validated addresses list endpoint"""
        # Create test addresses
        ValidatedAddress.objects.create(
            original_address='123 Test St',
            validation_status='valid'
        )
        ValidatedAddress.objects.create(
            original_address='456 Test Ave',
            validation_status='invalid'
        )
        
        url = '/api/address-validation/validated-addresses/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_validation_logs_list_endpoint(self):
        """Test validation logs list endpoint"""
        address = ValidatedAddress.objects.create(
            original_address='123 Test St'
        )
        
        AddressValidationLog.objects.create(
            address=address,
            validation_source='test',
            request_data={'address': '123 Test St'},
            response_data={'status': 'OK'},
            success=True,
            processing_time=0.1
        )
        
        url = '/api/address-validation/validation-logs/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['validation_source'], 'test')
    
    @patch('address_validation.views.get_validation_statistics')
    def test_statistics_endpoint_error_handling(self, mock_get_stats):
        """Test statistics endpoint error handling"""
        mock_get_stats.side_effect = Exception('Database error')
        
        url = '/api/address-validation/statistics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
