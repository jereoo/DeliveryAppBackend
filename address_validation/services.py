"""
Address Validation Services
Handles Google Maps API and Canada Post API integration
"""
import time
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
import googlemaps
import usaddress
import pycountry
from .models import ValidatedAddress, AddressValidationLog

logger = logging.getLogger(__name__)


class AddressValidationService:
    """Main service for address validation with LIVE Google Maps integration"""
    
    def __init__(self):
        """Initialize the address validation service with LIVE Google Maps client"""
        # Initialize Google Maps client with environment variable
        import os
        api_key = os.getenv('GOOGLE_MAPS_API_KEY') or getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        
        if api_key:
            try:
                import googlemaps
                self.google_client = googlemaps.Client(key=api_key)
                logger.info("Google Maps client initialized successfully")
            except ImportError:
                logger.error("googlemaps library not installed. Install with: pip install googlemaps")
                self.google_client = None
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
                self.google_client = None
        else:
            self.google_client = None
            logger.warning("GOOGLE_MAPS_API_KEY not configured - using basic validation only")
    
    def validate_address(self, address_text: str, country_hint: str = 'US') -> ValidatedAddress:
        """
        Validate address using appropriate service
        
        Args:
            address_text: Raw address string
            country_hint: Country code hint ('US', 'CA')
        
        Returns:
            ValidatedAddress object
        """
        # Create initial address record
        validated_address = ValidatedAddress.objects.create(
            original_address=address_text,
            validation_status='pending'
        )
        
        try:
            # Choose validation method based on country
            if country_hint.upper() == 'CA':
                self._validate_canadian_address(validated_address)
            else:
                self._validate_us_address(validated_address)
                
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            validated_address.validation_status = 'invalid'
            validated_address.save()
        
        return validated_address
    
    def _validate_us_address(self, address: ValidatedAddress) -> None:
        """Validate US address using usaddress parser and Google Maps API"""
        start_time = time.time()
        
        try:
            # First, parse with usaddress library
            parsed_address = self._parse_us_address(address.original_address)
            
            # Update address components
            self._update_address_components(address, parsed_address)
            
            # If Google Maps API is available, validate with it
            if self.google_client:
                self._validate_with_google_maps(address)
            else:
                # Use basic validation if no Google API
                address.validation_status = 'partial'
                address.validation_source = 'usaddress'
                address.confidence_score = 0.7
            
            address.save()
            
            # Log the validation attempt
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source=address.validation_source,
                request_data={'original_address': address.original_address},
                response_data=parsed_address,
                success=True,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source='usaddress',
                request_data={'original_address': address.original_address},
                response_data={},
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            raise e
    
    def _validate_canadian_address(self, address: ValidatedAddress) -> None:
        """Validate Canadian address using Canada Post API (placeholder)"""
        # TODO: Implement Canada Post API integration
        # For now, use basic parsing
        start_time = time.time()
        
        try:
            parsed_address = self._parse_us_address(address.original_address)  # Basic parsing
            self._update_address_components(address, parsed_address)
            
            address.validation_status = 'partial'
            address.validation_source = 'manual'
            address.confidence_score = 0.5
            address.country = 'Canada'
            address.save()
            
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source='canada_post',
                request_data={'original_address': address.original_address},
                response_data=parsed_address,
                success=True,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source='canada_post',
                request_data={'original_address': address.original_address},
                response_data={},
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            raise e
    
    def _parse_us_address(self, address_text: str) -> Dict:
        """Parse US address using usaddress library"""
        try:
            parsed, address_type = usaddress.tag(address_text)
            return {
                'street_number': parsed.get('AddressNumber', ''),
                'street_name': parsed.get('StreetName', ''),
                'street_type': parsed.get('StreetNamePostType', ''),
                'unit': parsed.get('OccupancyIdentifier', ''),
                'city': parsed.get('PlaceName', ''),
                'state': parsed.get('StateName', ''),
                'postal_code': parsed.get('ZipCode', ''),
                'address_type': address_type,
                'parsed_components': parsed
            }
        except Exception as e:
            logger.warning(f"Failed to parse address with usaddress: {e}")
            return {}
    
    def _validate_with_google_maps(self, address: ValidatedAddress) -> None:
        """Validate address using LIVE Google Maps Geocoding API"""
        start_time = time.time()
        
        try:
            # LIVE Google Maps Geocoding API call
            geocode_result = self.google_client.geocode(address.original_address)
            
            if geocode_result and len(geocode_result) > 0:
                result = geocode_result[0]
                
                # Extract coordinates
                location = result['geometry']['location']
                address.latitude = location['lat']
                address.longitude = location['lng']
                
                # Update normalized address
                address.normalized_address = result['formatted_address']
                
                # Extract address components
                components = result['address_components']
                self._parse_google_components(address, components)
                
                # Set validation status based on location type
                location_type = result['geometry'].get('location_type', 'APPROXIMATE')
                if location_type in ['ROOFTOP', 'RANGE_INTERPOLATED']:
                    address.validation_status = 'valid'
                    address.confidence_score = 0.95 if location_type == 'ROOFTOP' else 0.85
                else:
                    address.validation_status = 'partial'
                    address.confidence_score = 0.7
                    
                address.validation_source = 'google'
                
                # Log successful validation
                processing_time = time.time() - start_time
                AddressValidationLog.objects.create(
                    address=address,
                    validation_source='google',
                    request_data={'original_address': address.original_address},
                    response_data=result,
                    success=True,
                    processing_time=processing_time
                )
                
            else:
                # No results from Google - mark as invalid
                address.validation_status = 'invalid'
                address.validation_source = 'google'
                address.confidence_score = 0.0
                
                processing_time = time.time() - start_time
                AddressValidationLog.objects.create(
                    address=address,
                    validation_source='google',
                    request_data={'original_address': address.original_address},
                    response_data={'results': []},
                    success=False,
                    error_message='No geocoding results found',
                    processing_time=processing_time
                )
                
        except Exception as e:
            logger.error(f"Google Maps validation failed: {e}")
            processing_time = time.time() - start_time
            
            # Log the error
            AddressValidationLog.objects.create(
                address=address,
                validation_source='google',
                request_data={'original_address': address.original_address},
                response_data={},
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            # Fall back to usaddress parsing
            logger.info(f"Falling back to usaddress parsing for: {address.original_address}")
            parsed_address = self._parse_us_address(address.original_address)
            self._update_address_components(address, parsed_address)
            address.validation_status = 'partial'
            address.validation_source = 'usaddress'
            address.confidence_score = 0.6
    
    def _parse_google_components(self, address: ValidatedAddress, components: list) -> None:
        """Parse Google Maps address components"""
        for component in components:
            types = component['types']
            long_name = component['long_name']
            short_name = component['short_name']
            
            if 'street_number' in types:
                address.street_number = long_name
            elif 'route' in types:
                address.street_name = long_name
            elif 'subpremise' in types:
                address.unit = long_name
            elif 'locality' in types:
                address.city = long_name
            elif 'administrative_area_level_1' in types:
                address.state_province = short_name
            elif 'postal_code' in types:
                address.postal_code = long_name
            elif 'country' in types:
                address.country = long_name
    
    def _update_address_components(self, address: ValidatedAddress, parsed_data: Dict) -> None:
        """Update address object with parsed components"""
        if not parsed_data:
            return
        
        address.street_number = parsed_data.get('street_number', '')
        address.street_name = parsed_data.get('street_name', '')
        address.street_type = parsed_data.get('street_type', '')
        address.unit = parsed_data.get('unit', '')
        address.city = parsed_data.get('city', '')
        address.state_province = parsed_data.get('state', '')
        address.postal_code = parsed_data.get('postal_code', '')
        
        # Build normalized address
        address.normalized_address = address.formatted_address


# Convenience functions
def validate_address(address_text: str, country_hint: str = 'US') -> ValidatedAddress:
    """Convenience function to validate an address"""
    service = AddressValidationService()
    return service.validate_address(address_text, country_hint)


def get_validation_statistics() -> Dict:
    """Get address validation statistics"""
    from django.db.models import Count, Q
    
    stats = ValidatedAddress.objects.aggregate(
        total=Count('id'),
        valid=Count('id', filter=Q(validation_status='valid')),
        invalid=Count('id', filter=Q(validation_status='invalid')),
        partial=Count('id', filter=Q(validation_status='partial')),
        pending=Count('id', filter=Q(validation_status='pending'))
    )
    
    # Calculate percentages
    total = stats['total']
    if total > 0:
        stats['valid_percentage'] = (stats['valid'] / total) * 100
        stats['success_rate'] = ((stats['valid'] + stats['partial']) / total) * 100
    else:
        stats['valid_percentage'] = 0
        stats['success_rate'] = 0
    
    return stats