# ENFORCED BY CIO DIRECTIVE – CORRECT DIRECTORY – NOV 20 2025
"""
Enhanced address validation tests with live Google Maps API mocking
Tests both live API integration and fallback scenarios
"""
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import responses
from .models import ValidatedAddress, AddressValidationLog
from .live_services import AddressValidationService, LiveGoogleMapsService
from .services import validate_address, get_validation_statistics
from .serializers import (
    ValidatedAddressSerializer, 
    AddressValidationLogSerializer,
    AddressValidationRequestSerializer
)


class LiveGoogleMapsServiceTests(TestCase):
    """Test live Google Maps service integration"""
    
    def setUp(self):
        """Set up test environment with mock API key"""
        with patch.dict('os.environ', {'GOOGLE_MAPS_API_KEY': 'test-api-key'}):
            with patch('address_validation.live_services.googlemaps.Client') as mock_client:
                mock_client.return_value = MagicMock()
                self.service = LiveGoogleMapsService()
    
    @patch('address_validation.live_services.googlemaps.Client')
    def test_service_initialization_success(self, mock_client):
        """Test successful service initialization"""
        mock_client.return_value = MagicMock()
        
        with patch.dict('os.environ', {'GOOGLE_MAPS_API_KEY': 'test-key'}):
            service = LiveGoogleMapsService()
            self.assertIsNotNone(service.client)
            mock_client.assert_called_once_with(key='test-key')
    
    def test_service_initialization_no_api_key(self):
        """Test service initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                LiveGoogleMapsService()
    
    def test_geocode_address_success(self):
        """Test successful address geocoding"""
        # Mock successful geocoding response
        mock_result = {
            'geometry': {
                'location': {'lat': 40.7128, 'lng': -74.0060},
                'location_type': 'ROOFTOP'
            },
            'formatted_address': '123 Main St, New York, NY 10001, USA',
            'address_components': [
                {
                    'long_name': '123',
                    'short_name': '123',
                    'types': ['street_number']
                },
                {
                    'long_name': 'Main Street',
                    'short_name': 'Main St',
                    'types': ['route']
                }
            ]
        }
        
        self.service.client.geocode.return_value = [mock_result]
        
        result = self.service.geocode_address('123 Main St, New York, NY')
        
        self.assertEqual(result, mock_result)
        self.service.client.geocode.assert_called_once_with('123 Main St, New York, NY')
    
    def test_geocode_address_no_results(self):
        """Test geocoding with no results"""
        self.service.client.geocode.return_value = []
        
        result = self.service.geocode_address('Invalid Address')
        
        self.assertIsNone(result)
    
    def test_places_autocomplete_success(self):
        """Test successful places autocomplete"""
        mock_predictions = [
            {
                'description': '123 Main Street, New York, NY, USA',
                'place_id': 'ChIJd8BlQ2BZwokRAFUEcm_qrcA'
            }
        ]
        
        self.service.client.places_autocomplete.return_value = mock_predictions
        
        result = self.service.places_autocomplete('123 Main', 'us')
        
        self.assertEqual(result, mock_predictions)
        self.service.client.places_autocomplete.assert_called_once_with(
            input_text='123 Main',
            components={'country': 'us'},
            types=['address']
        )


class LiveAddressValidationServiceTests(TestCase):
    """Test enhanced address validation service with live Google Maps"""
    
    def setUp(self):
        """Set up test service with mocked Google Maps"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Mock Google Maps service
        self.mock_google_service = Mock()
        self.service = AddressValidationService()
        self.service.google_service = self.mock_google_service
    
    def test_validate_us_address_with_google_success(self):
        """Test successful US address validation with Google Maps"""
        # Mock Google geocoding response
        mock_geocode_result = {
            'geometry': {
                'location': {'lat': 40.7128, 'lng': -74.0060},
                'location_type': 'ROOFTOP'
            },
            'formatted_address': '123 Main St, New York, NY 10001, USA',
            'address_components': [
                {
                    'long_name': '123',
                    'short_name': '123',
                    'types': ['street_number']
                },
                {
                    'long_name': 'Main Street',
                    'short_name': 'Main St',
                    'types': ['route']
                },
                {
                    'long_name': 'New York',
                    'short_name': 'New York',
                    'types': ['locality']
                },
                {
                    'long_name': 'New York',
                    'short_name': 'NY',
                    'types': ['administrative_area_level_1']
                },
                {
                    'long_name': '10001',
                    'short_name': '10001',
                    'types': ['postal_code']
                }
            ]
        }
        
        self.mock_google_service.geocode_address.return_value = mock_geocode_result
        
        result = self.service.validate_address('123 Main St, New York, NY', 'US')
        
        self.assertIsInstance(result, ValidatedAddress)
        self.assertEqual(result.original_address, '123 Main St, New York, NY')
        self.assertEqual(result.validation_status, 'valid')
        self.assertEqual(result.validation_source, 'google')
        self.assertEqual(result.confidence_score, 0.95)
        self.assertEqual(result.latitude, 40.7128)
        self.assertEqual(result.longitude, -74.0060)
        self.assertEqual(result.street_number, '123')
        self.assertEqual(result.street_name, 'Main Street')
        self.assertEqual(result.city, 'New York')
        self.assertEqual(result.state_province, 'NY')
        self.assertEqual(result.postal_code, '10001')
    
    def test_validate_canadian_address_with_google(self):
        """Test Canadian address validation with Google Maps"""
        mock_geocode_result = {
            'geometry': {
                'location': {'lat': 43.6532, 'lng': -79.3832},
                'location_type': 'RANGE_INTERPOLATED'
            },
            'formatted_address': '123 Main St, Toronto, ON M5V 3A8, Canada',
            'address_components': [
                {
                    'long_name': '123',
                    'short_name': '123',
                    'types': ['street_number']
                },
                {
                    'long_name': 'Main Street',
                    'short_name': 'Main St',
                    'types': ['route']
                },
                {
                    'long_name': 'Toronto',
                    'short_name': 'Toronto',
                    'types': ['locality']
                },
                {
                    'long_name': 'Ontario',
                    'short_name': 'ON',
                    'types': ['administrative_area_level_1']
                },
                {
                    'long_name': 'M5V 3A8',
                    'short_name': 'M5V 3A8',
                    'types': ['postal_code']
                },
                {
                    'long_name': 'Canada',
                    'short_name': 'CA',
                    'types': ['country']
                }
            ]
        }
        
        self.mock_google_service.geocode_address.return_value = mock_geocode_result
        
        result = self.service.validate_address('123 Main St, Toronto, ON', 'CA')
        
        self.assertEqual(result.validation_status, 'valid')  # RANGE_INTERPOLATED
        self.assertEqual(result.validation_source, 'google')
        self.assertEqual(result.confidence_score, 0.85)
        self.assertEqual(result.country, 'Canada')
    
    def test_validate_address_google_failure_fallback(self):
        """Test fallback to usaddress when Google Maps fails"""
        # Mock Google service to raise exception
        self.mock_google_service.geocode_address.side_effect = Exception('API quota exceeded')
        
        with patch('address_validation.live_services.PARSING_LIBRARIES_AVAILABLE', True):
            with patch('address_validation.live_services.usaddress.tag') as mock_tag:
                mock_tag.return_value = (
                    {
                        'AddressNumber': '456',
                        'StreetName': 'Oak',
                        'StreetNamePostType': 'Ave',
                        'PlaceName': 'Boston',
                        'StateName': 'MA',
                        'ZipCode': '02101'
                    },
                    'Street Address'
                )
                
                result = self.service.validate_address('456 Oak Ave, Boston, MA', 'US')
                
                self.assertEqual(result.validation_status, 'partial')
                self.assertEqual(result.validation_source, 'usaddress')
                self.assertEqual(result.confidence_score, 0.6)
                self.assertEqual(result.street_number, '456')
                self.assertEqual(result.street_name, 'Oak')
    
    def test_validate_address_no_google_service(self):
        """Test validation when Google service is unavailable"""
        self.service.google_service = None
        
        with patch('address_validation.live_services.PARSING_LIBRARIES_AVAILABLE', True):
            with patch('address_validation.live_services.usaddress.tag') as mock_tag:
                mock_tag.return_value = (
                    {
                        'AddressNumber': '789',
                        'StreetName': 'Pine',
                        'StreetNamePostType': 'St'
                    },
                    'Street Address'
                )
                
                result = self.service.validate_address('789 Pine St', 'US')
                
                self.assertEqual(result.validation_status, 'partial')
                self.assertEqual(result.validation_source, 'usaddress')
    
    def test_validation_logging_success(self):
        """Test that successful validations are properly logged"""
        mock_geocode_result = {
            'geometry': {
                'location': {'lat': 40.7128, 'lng': -74.0060},
                'location_type': 'ROOFTOP'
            },
            'formatted_address': '123 Test St, New York, NY 10001, USA',
            'address_components': []
        }
        
        self.mock_google_service.geocode_address.return_value = mock_geocode_result
        
        result = self.service.validate_address('123 Test St, New York, NY', 'US')
        
        # Verify log was created
        log = AddressValidationLog.objects.filter(address=result).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.success)
        self.assertEqual(log.validation_source, 'google')
        self.assertGreater(log.processing_time, 0)
    
    def test_validation_logging_failure(self):
        """Test that failed validations are properly logged"""
        self.mock_google_service.geocode_address.return_value = None
        
        result = self.service.validate_address('Invalid Address', 'US')
        
        # Verify error log was created
        log = AddressValidationLog.objects.filter(address=result).first()
        self.assertIsNotNone(log)
        self.assertFalse(log.success)
        self.assertEqual(log.error_message, 'No geocoding results found')


class LiveAddressValidationAPITests(APITestCase):
    """Test API endpoints with live Google Maps integration"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    @patch('address_validation.views.validate_address')
    def test_validate_endpoint_with_live_google_maps(self, mock_validate):
        """Test validation endpoint using live Google Maps service"""
        # Mock the live validation service
        mock_address = ValidatedAddress.objects.create(
            original_address='123 Live Test St',
            validation_status='valid',
            validation_source='google',
            confidence_score=0.95,
            latitude=40.7128,
            longitude=-74.0060
        )
        mock_validate.return_value = mock_address
        
        url = '/api/address-validation/validate/'
        data = {
            'address': '123 Live Test St, New York, NY',
            'country_hint': 'US'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['validation_source'], 'google')
        self.assertEqual(response.data['confidence_score'], 0.95)
        self.assertIsNotNone(response.data['latitude'])
        self.assertIsNotNone(response.data['longitude'])
    
    @responses.activate
    def test_places_autocomplete_endpoint(self):
        """Test places autocomplete endpoint (if implemented)"""
        # Mock Google Places API response
        responses.add(
            responses.GET,
            'https://maps.googleapis.com/maps/api/place/autocomplete/json',
            json={
                'predictions': [
                    {
                        'description': '123 Main Street, New York, NY, USA',
                        'place_id': 'ChIJd8BlQ2BZwokRAFUEcm_qrcA'
                    }
                ],
                'status': 'OK'
            },
            status=200
        )
        
        # Test autocomplete endpoint if it exists
        # This would require implementing the endpoint in views.py
        pass


class LiveValidationStatisticsTests(TestCase):
    """Test validation statistics with live Google Maps data"""
    
    def test_statistics_with_google_validations(self):
        """Test statistics calculation with Google Maps validations"""
        # Create test data with different validation sources
        ValidatedAddress.objects.create(
            original_address='Google Valid 1',
            validation_status='valid',
            validation_source='google',
            confidence_score=0.95
        )
        ValidatedAddress.objects.create(
            original_address='Google Valid 2',
            validation_status='valid',
            validation_source='google',
            confidence_score=0.90
        )
        ValidatedAddress.objects.create(
            original_address='usaddress Partial',
            validation_status='partial',
            validation_source='usaddress',
            confidence_score=0.6
        )
        ValidatedAddress.objects.create(
            original_address='Invalid Address',
            validation_status='invalid',
            validation_source='google',
            confidence_score=0.0
        )
        
        stats = get_validation_statistics()
        
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['valid'], 2)
        self.assertEqual(stats['partial'], 1)
        self.assertEqual(stats['invalid'], 1)
        self.assertEqual(stats['success_rate'], 75.0)  # (2+1)/4 * 100


class LiveGoogleMapsIntegrationTests(TestCase):
    """Integration tests with live Google Maps API (requires API key)"""
    
    def setUp(self):
        """Set up integration tests (skipped if no API key)"""
        import os
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            self.skipTest("GOOGLE_MAPS_API_KEY not set - skipping live integration tests")
    
    def test_live_geocoding_integration(self):
        """Test actual geocoding with Google Maps API"""
        # This test makes a real API call - use sparingly
        service = LiveGoogleMapsService()
        
        # Test with a well-known address
        result = service.geocode_address('1600 Amphitheatre Parkway, Mountain View, CA')
        
        self.assertIsNotNone(result)
        self.assertIn('geometry', result)
        self.assertIn('location', result['geometry'])
        self.assertIn('formatted_address', result)
    
    def test_live_places_autocomplete_integration(self):
        """Test actual places autocomplete with Google Maps API"""
        service = LiveGoogleMapsService()
        
        # Test with partial address
        results = service.places_autocomplete('1600 Amphitheatre', 'us')
        
        self.assertIsInstance(results, list)
        if results:  # If API returns results
            self.assertIn('description', results[0])
            self.assertIn('place_id', results[0])


# Backward compatibility tests
class BackwardCompatibilityTests(TestCase):
    """Test that existing code still works with live Google Maps integration"""
    
    @patch('address_validation.services.AddressValidationService')
    def test_validate_address_function_compatibility(self, mock_service_class):
        """Test that the validate_address function still works"""
        mock_service = Mock()
        mock_service.validate_address.return_value = ValidatedAddress.objects.create(
            original_address='Test Address',
            validation_status='valid'
        )
        mock_service_class.return_value = mock_service
        
        # Import from original services module
        from .services import validate_address as legacy_validate_address
        
        result = legacy_validate_address('Test Address', 'US')
        
        self.assertIsInstance(result, ValidatedAddress)
        self.assertEqual(result.validation_status, 'valid')