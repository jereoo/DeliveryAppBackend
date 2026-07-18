"""Driver license format validation for US states and Canadian provinces."""
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from delivery.driver_license_validation import (
    list_license_regions,
    normalize_license_number,
    validate_driver_license_number,
)


class DriverLicenseValidationTests(SimpleTestCase):
    def test_list_license_regions_includes_all_ca_and_us(self):
        regions = list_license_regions()
        ca_codes = {region['code'] for region in regions if region['country'] == 'CA'}
        us_codes = {region['code'] for region in regions if region['country'] == 'US'}
        self.assertEqual(len(ca_codes), 13)
        self.assertEqual(len(us_codes), 51)

    def test_bc_valid_seven_digits(self):
        normalized = validate_driver_license_number('CA-BC', '1234567')
        self.assertEqual(normalized, '1234567')

    def test_bc_normalizes_spaces_and_dashes(self):
        normalized = validate_driver_license_number('CA-BC', '123-45 67')
        self.assertEqual(normalized, '1234567')

    def test_us_ca_valid_format(self):
        normalized = validate_driver_license_number('US-CA', 'a1234567')
        self.assertEqual(normalized, 'A1234567')

    def test_invalid_region_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_driver_license_number('XX-YY', '1234567')
        self.assertIn('license_issuing_region', ctx.exception.message_dict)

    def test_invalid_bc_format_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_driver_license_number('CA-BC', '12345')
        self.assertIn('license_number', ctx.exception.message_dict)

    def test_normalize_license_number(self):
        self.assertEqual(normalize_license_number(' ab-12 cd '), 'AB12CD')
