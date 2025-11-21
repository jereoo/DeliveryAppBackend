# ENFORCED BY CIO DIRECTIVE – CORRECT DIRECTORY – NOV 20 2025
"""
Live Google Maps Address Validation Integration
Replaces mock implementation with real Google Maps Geocoding API calls
"""
import logging
import time
import os
from typing import Dict, Optional
from django.conf import settings
from django.db.models import Q
from .models import ValidatedAddress, AddressValidationLog

logger = logging.getLogger(__name__)

# Import Google Maps client (install with: pip install googlemaps)
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    logger.warning("googlemaps library not installed. Install with: pip install googlemaps")

# Import address parsing libraries
try:
    import usaddress
    import pycountry
    PARSING_LIBRARIES_AVAILABLE = True
except ImportError:
    PARSING_LIBRARIES_AVAILABLE = False
    logger.error("Address parsing libraries not available")


class LiveGoogleMapsService:
    """Live Google Maps Geocoding and Places API integration"""
    
    def __init__(self):
        """Initialize with live Google Maps API key"""
        api_key = os.getenv('GOOGLE_MAPS_API_KEY') or getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        
        if not api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")
            
        if not GOOGLEMAPS_AVAILABLE:
            raise ImportError("googlemaps library not installed. Run: pip install googlemaps")
            
        try:
            self.client = googlemaps.Client(key=api_key)
            logger.info("Google Maps client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps client: {e}")
            raise
    
    def geocode_address(self, address_text: str) -> Optional[Dict]:
        """Geocode address using Google Maps Geocoding API"""
        try:
            results = self.client.geocode(address_text)
            if results and len(results) > 0:
                return results[0]
            return None
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Maps API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            raise
    
    def places_autocomplete(self, input_text: str, country_code: str = 'us') -> list:
        """Get place predictions using Google Places API"""
        try:
            predictions = self.client.places_autocomplete(
                input_text=input_text,
                components={'country': country_code},
                types=['address']
            )
            return predictions
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Places API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Places autocomplete failed: {e}")
            raise


class AddressValidationService:
    """Enhanced address validation service with live Google Maps integration"""
    
    def __init__(self):
        """Initialize with live Google Maps service and fallback options"""
        self.google_service = None
        
        # Try to initialize Google Maps service
        try:
            self.google_service = LiveGoogleMapsService()
        except (ValueError, ImportError) as e:
            logger.warning(f"Google Maps service unavailable: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps service: {e}")
    
    def validate_address(self, address_text: str, country_hint: str = 'US') -> ValidatedAddress:
        """
        Validate address with live Google Maps API and fallback options
        
        Args:
            address_text: Raw address string
            country_hint: Country code hint ('US', 'CA', etc.)
            
        Returns:
            ValidatedAddress instance with validation results
        """
        # Create address record
        validated_address = ValidatedAddress.objects.create(
            original_address=address_text,
            validation_status='pending'
        )
        
        try:
            # Determine country for validation
            country_upper = country_hint.upper()
            if country_upper == 'CA':
                validated_address.country = 'Canada'
                self._validate_canadian_address(validated_address)
            else:
                validated_address.country = 'United States'
                self._validate_us_address(validated_address)
                
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            validated_address.validation_status = 'invalid'
            validated_address.save()
        
        return validated_address
    
    def _validate_us_address(self, address: ValidatedAddress) -> None:
        """Validate US address with Google Maps and usaddress fallback"""
        start_time = time.time()
        
        try:
            # Primary: Try Google Maps validation
            if self.google_service:
                self._validate_with_live_google_maps(address)
            else:
                # Fallback: Parse with usaddress library
                self._validate_with_usaddress(address)
            
            address.save()
            
        except Exception as e:
            # Log error and fall back to basic parsing
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source='error_fallback',
                request_data={'original_address': address.original_address},
                response_data={},
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            # Try usaddress as final fallback
            try:
                self._validate_with_usaddress(address)
                address.save()
            except Exception as fallback_error:
                logger.error(f"All validation methods failed: {fallback_error}")
                address.validation_status = 'invalid'
                address.save()
    
    def _validate_canadian_address(self, address: ValidatedAddress) -> None:
        """Validate Canadian address with Google Maps and basic parsing fallback"""
        start_time = time.time()
        
        try:
            # Primary: Try Google Maps validation
            if self.google_service:
                self._validate_with_live_google_maps(address)
            else:
                # Fallback: Basic parsing for Canadian addresses
                self._validate_with_basic_parsing(address)
            
            address.save()
            
        except Exception as e:
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source='canada_fallback',
                request_data={'original_address': address.original_address},
                response_data={},
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            # Set partial status for Canadian addresses
            address.validation_status = 'partial'
            address.validation_source = 'manual'
            address.confidence_score = 0.5
            address.save()
    
    def _validate_with_live_google_maps(self, address: ValidatedAddress) -> None:
        """Validate address using LIVE Google Maps Geocoding API"""
        start_time = time.time()
        
        try:
            # Make live API call to Google Maps
            result = self.google_service.geocode_address(address.original_address)
            
            if result:
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
            
            # Re-raise to trigger fallback
            raise
    
    def _validate_with_usaddress(self, address: ValidatedAddress) -> None:
        """Fallback validation using usaddress library"""
        if not PARSING_LIBRARIES_AVAILABLE:
            raise ImportError("usaddress library not available")
            
        start_time = time.time()
        
        try:
            parsed_address = self._parse_us_address(address.original_address)
            self._update_address_components(address, parsed_address)
            
            address.validation_status = 'partial'
            address.validation_source = 'usaddress'
            address.confidence_score = 0.6
            
            processing_time = time.time() - start_time
            AddressValidationLog.objects.create(
                address=address,
                validation_source='usaddress',
                request_data={'original_address': address.original_address},
                response_data=parsed_address,
                success=True,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"usaddress parsing failed: {e}")
            raise
    
    def _validate_with_basic_parsing(self, address: ValidatedAddress) -> None:
        """Basic parsing for Canadian addresses"""
        start_time = time.time()
        
        # Simple parsing for Canadian addresses
        address.validation_status = 'partial'
        address.validation_source = 'manual'
        address.confidence_score = 0.5
        
        processing_time = time.time() - start_time
        AddressValidationLog.objects.create(
            address=address,
            validation_source='canada_basic',
            request_data={'original_address': address.original_address},
            response_data={'parsing_method': 'basic'},
            success=True,
            processing_time=processing_time
        )
    
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


# Convenience functions for backward compatibility
def validate_address(address_text: str, country_hint: str = 'US') -> ValidatedAddress:
    """Convenience function to validate an address with live Google Maps"""
    service = AddressValidationService()
    return service.validate_address(address_text, country_hint)


def get_validation_statistics() -> Dict:
    """Get address validation statistics"""
    from django.db.models import Count
    
    stats = ValidatedAddress.objects.aggregate(
        total=Count('id'),
        valid=Count('id', filter=Q(validation_status='valid')),
        invalid=Count('id', filter=Q(validation_status='invalid')),
        partial=Count('id', filter=Q(validation_status='partial')),
        pending=Count('id', filter=Q(validation_status='pending'))
    )
    
    total = stats['total']
    if total > 0:
        stats['valid_percentage'] = round((stats['valid'] / total) * 100, 1)
        stats['success_rate'] = round(((stats['valid'] + stats['partial']) / total) * 100, 1)
    else:
        stats['valid_percentage'] = 0
        stats['success_rate'] = 0
    
    return stats


def get_places_autocomplete(input_text: str, country_code: str = 'us') -> list:
    """Get Google Places autocomplete suggestions"""
    try:
        service = LiveGoogleMapsService()
        return service.places_autocomplete(input_text, country_code)
    except Exception as e:
        logger.error(f"Places autocomplete failed: {e}")
        return []