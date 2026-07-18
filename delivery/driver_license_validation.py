"""Driver license format validation for US states and Canadian provinces (NTSI-based patterns)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from django.core.exceptions import ValidationError


@dataclass(frozen=True)
class LicenseRegionRule:
    code: str
    name: str
    country: str
    patterns: tuple[str, ...]
    hint: str


def normalize_license_number(value: str) -> str:
    """Strip spaces/dashes and uppercase for comparison."""
    return re.sub(r'[\s\-]', '', (value or '').strip().upper())


def _compile_patterns(patterns: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern) for pattern in patterns)


# NTSI / common format summaries — patterns applied after normalize_license_number().
_LICENSE_REGIONS: tuple[LicenseRegionRule, ...] = (
    # Canada
    LicenseRegionRule('CA-AB', 'Alberta', 'CA', (r'^\d{5,9}$', r'^\d{6}\d{3}$'), '5-9 digits'),
    LicenseRegionRule('CA-BC', 'British Columbia', 'CA', (r'^\d{7}$',), '7 digits'),
    LicenseRegionRule('CA-MB', 'Manitoba', 'CA', (r'^[A-Z0-9]{7,12}$',), '7-12 letters or digits'),
    LicenseRegionRule('CA-NB', 'New Brunswick', 'CA', (r'^\d{5,7}$',), '5-7 digits'),
    LicenseRegionRule('CA-NL', 'Newfoundland and Labrador', 'CA', (r'^[A-Z]\d{9}$',), '1 letter + 9 digits'),
    LicenseRegionRule('CA-NS', 'Nova Scotia', 'CA', (r'^[A-Z0-9]{10,12}$',), '10-12 letters or digits'),
    LicenseRegionRule('CA-NT', 'Northwest Territories', 'CA', (r'^\d{6}$',), '6 digits'),
    LicenseRegionRule('CA-NU', 'Nunavut', 'CA', (r'^\d{5,6}$',), '5-6 digits'),
    LicenseRegionRule(
        'CA-ON', 'Ontario', 'CA',
        (r'^[A-Z]\d{14}$', r'^[A-Z0-9]{15,17}$'),
        '1 letter + 14 digits (dashes optional)',
    ),
    LicenseRegionRule('CA-PE', 'Prince Edward Island', 'CA', (r'^\d{5,6}$',), '5-6 digits'),
    LicenseRegionRule('CA-QC', 'Quebec', 'CA', (r'^[A-Z]\d{12}$', r'^[A-Z0-9]{8,13}$'), 'Letter(s) + digits'),
    LicenseRegionRule('CA-SK', 'Saskatchewan', 'CA', (r'^\d{8}$',), '8 digits'),
    LicenseRegionRule('CA-YT', 'Yukon', 'CA', (r'^\d{1,6}$',), '1-6 digits'),
    # United States
    LicenseRegionRule('US-AL', 'Alabama', 'US', (r'^\d{1,8}$',), '1-8 digits'),
    LicenseRegionRule('US-AK', 'Alaska', 'US', (r'^\d{1,7}$',), '1-7 digits'),
    LicenseRegionRule('US-AZ', 'Arizona', 'US', (r'^[A-Z0-9]\d{8}$', r'^\d{9}$'), '1 letter/digit + 8 digits'),
    LicenseRegionRule('US-AR', 'Arkansas', 'US', (r'^\d{4,9}$',), '4-9 digits'),
    LicenseRegionRule('US-CA', 'California', 'US', (r'^[A-Z]\d{7}$',), '1 letter + 7 digits'),
    LicenseRegionRule('US-CO', 'Colorado', 'US', (r'^\d{9}$', r'^[A-Z]\d{3,6}$', r'^[A-Z]{2}\d{2,5}$'), '9 digits or letter(s) + digits'),
    LicenseRegionRule('US-CT', 'Connecticut', 'US', (r'^\d{9}$',), '9 digits'),
    LicenseRegionRule('US-DE', 'Delaware', 'US', (r'^\d{1,7}$',), '1-7 digits'),
    LicenseRegionRule('US-DC', 'District of Columbia', 'US', (r'^\d{7}$', r'^\d{9}$'), '7 or 9 digits'),
    LicenseRegionRule('US-FL', 'Florida', 'US', (r'^[A-Z]\d{12}$',), '1 letter + 12 digits'),
    LicenseRegionRule('US-GA', 'Georgia', 'US', (r'^\d{7,9}$',), '7-9 digits'),
    LicenseRegionRule('US-HI', 'Hawaii', 'US', (r'^[A-Z]\d{8}$', r'^\d{9}$'), '1 letter + 8 digits or 9 digits'),
    LicenseRegionRule('US-ID', 'Idaho', 'US', (r'^[A-Z]{2}\d{6}[A-Z]$', r'^\d{9}$'), '2 letters + 6 digits + letter, or 9 digits'),
    LicenseRegionRule('US-IL', 'Illinois', 'US', (r'^[A-Z]\d{11,12}$',), '1 letter + 11-12 digits'),
    LicenseRegionRule('US-IN', 'Indiana', 'US', (r'^[A-Z]\d{9}$', r'^\d{10}$'), '1 letter + 9 digits or 10 digits'),
    LicenseRegionRule('US-IA', 'Iowa', 'US', (r'^\d{9}$', r'^\d{3}[A-Z]{2}\d{4}$'), '9 digits or 3 digits + 2 letters + 4 digits'),
    LicenseRegionRule('US-KS', 'Kansas', 'US', (r'^[A-Z]\d[A-Z]\d[A-Z]$', r'^[A-Z]\d{8}$', r'^\d{9}$'), 'Letter/digit pattern or 9 digits'),
    LicenseRegionRule('US-KY', 'Kentucky', 'US', (r'^[A-Z]\d{8,9}$', r'^\d{9}$'), '1 letter + 8-9 digits or 9 digits'),
    LicenseRegionRule('US-LA', 'Louisiana', 'US', (r'^\d{1,9}$',), '1-9 digits'),
    LicenseRegionRule('US-ME', 'Maine', 'US', (r'^\d{7}$', r'^\d{7}[A-Z]$', r'^\d{8}$'), '7-8 digits'),
    LicenseRegionRule('US-MD', 'Maryland', 'US', (r'^[A-Z]\d{12}$',), '1 letter + 12 digits'),
    LicenseRegionRule('US-MA', 'Massachusetts', 'US', (r'^[A-Z]\d{8}$', r'^\d{9}$', r'^SA\d{7}$'), '1 letter + 8 digits, 9 digits, or SA + 7 digits'),
    LicenseRegionRule('US-MI', 'Michigan', 'US', (r'^[A-Z]\d{10}$', r'^[A-Z]\d{12}$'), '1 letter + 10 or 12 digits'),
    LicenseRegionRule('US-MN', 'Minnesota', 'US', (r'^[A-Z]\d{12}$',), '1 letter + 12 digits'),
    LicenseRegionRule('US-MS', 'Mississippi', 'US', (r'^\d{9}$',), '9 digits'),
    LicenseRegionRule('US-MO', 'Missouri', 'US', (r'^\d{3}[A-Z]\d{6}$', r'^[A-Z]\d{5,9}$', r'^\d{8}[A-Z]{2}$', r'^\d{9}[A-Z]?$'), 'Mixed letter/digit formats'),
    LicenseRegionRule('US-MT', 'Montana', 'US', (r'^[A-Z]\d{8}$', r'^\d{9}$', r'^\d{13,14}$'), 'Letter + digits or 9-14 digits'),
    LicenseRegionRule('US-NE', 'Nebraska', 'US', (r'^[A-Z]\d{6,8}$',), '1 letter + 6-8 digits'),
    LicenseRegionRule('US-NV', 'Nevada', 'US', (r'^\d{9,10}$', r'^\d{12}$', r'^[X]\d{8}$'), '9-12 digits or X + 8 digits'),
    LicenseRegionRule('US-NH', 'New Hampshire', 'US', (r'^\d{2}[A-Z]{3}\d{5}$',), '2 digits + 3 letters + 5 digits'),
    LicenseRegionRule('US-NJ', 'New Jersey', 'US', (r'^[A-Z]\d{14}$',), '1 letter + 14 digits'),
    LicenseRegionRule('US-NM', 'New Mexico', 'US', (r'^\d{8,9}$',), '8-9 digits'),
    LicenseRegionRule('US-NY', 'New York', 'US', (r'^[A-Z]\d{7}$', r'^[A-Z]\d{18}$', r'^\d{8,9}$', r'^\d{16}$', r'^[A-Z]{8}$'), 'Multiple NY formats'),
    LicenseRegionRule('US-NC', 'North Carolina', 'US', (r'^\d{1,12}$',), '1-12 digits'),
    LicenseRegionRule('US-ND', 'North Dakota', 'US', (r'^[A-Z]{3}\d{6}$', r'^\d{9}$'), '3 letters + 6 digits or 9 digits'),
    LicenseRegionRule('US-OH', 'Ohio', 'US', (r'^[A-Z]\d{4,8}$', r'^[A-Z]{2}\d{3,7}$', r'^\d{8}$'), 'Letter(s) + digits or 8 digits'),
    LicenseRegionRule('US-OK', 'Oklahoma', 'US', (r'^[A-Z]?\d{9}$',), 'Optional letter + 9 digits'),
    LicenseRegionRule('US-OR', 'Oregon', 'US', (r'^\d{1,9}$',), '1-9 digits'),
    LicenseRegionRule('US-PA', 'Pennsylvania', 'US', (r'^\d{8}$',), '8 digits'),
    LicenseRegionRule('US-RI', 'Rhode Island', 'US', (r'^\d{7}$', r'^[A-Z]\d{6}$'), '7 digits or 1 letter + 6 digits'),
    LicenseRegionRule('US-SC', 'South Carolina', 'US', (r'^\d{5,11}$',), '5-11 digits'),
    LicenseRegionRule('US-SD', 'South Dakota', 'US', (r'^\d{6,10}$', r'^\d{12}$'), '6-12 digits'),
    LicenseRegionRule('US-TN', 'Tennessee', 'US', (r'^\d{7,9}$',), '7-9 digits'),
    LicenseRegionRule('US-TX', 'Texas', 'US', (r'^\d{7,8}$',), '7-8 digits'),
    LicenseRegionRule('US-UT', 'Utah', 'US', (r'^\d{4,10}$',), '4-10 digits'),
    LicenseRegionRule('US-VT', 'Vermont', 'US', (r'^\d{8}$', r'^\d{7}A$'), '8 digits or 7 digits + A'),
    LicenseRegionRule('US-VA', 'Virginia', 'US', (r'^[A-Z]\d{8,11}$', r'^\d{9}$'), '1 letter + 8-11 digits or 9 digits'),
    LicenseRegionRule('US-WA', 'Washington', 'US', (r'^[A-Z0-9]{12}$',), '12 letters or digits'),
    LicenseRegionRule('US-WV', 'West Virginia', 'US', (r'^\d{7}$', r'^[A-Z]{1,2}\d{5,6}$'), '7 digits or letter(s) + digits'),
    LicenseRegionRule('US-WI', 'Wisconsin', 'US', (r'^[A-Z]\d{13}$',), '1 letter + 13 digits'),
    LicenseRegionRule('US-WY', 'Wyoming', 'US', (r'^\d{9,10}$',), '9-10 digits'),
)

LICENSE_REGION_BY_CODE: dict[str, LicenseRegionRule] = {
    rule.code: rule for rule in _LICENSE_REGIONS
}

_COMPILED_REGION_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    code: _compile_patterns(rule.patterns)
    for code, rule in LICENSE_REGION_BY_CODE.items()
}


def list_license_regions(*, country: str | None = None) -> list[dict[str, str]]:
    """Return region metadata for API/UI pickers."""
    regions = _LICENSE_REGIONS
    if country:
        regions = tuple(r for r in regions if r.country == country.upper())
    return [
        {'code': rule.code, 'name': rule.name, 'country': rule.country, 'hint': rule.hint}
        for rule in regions
    ]


def get_license_region_hint(region_code: str) -> str:
    rule = LICENSE_REGION_BY_CODE.get(region_code)
    return rule.hint if rule else ''


def validate_driver_license_number(region_code: str, license_number: str) -> str:
    """
    Validate and normalize a driver license number for the given region code.

    Raises ValidationError when the region or format is invalid.
    Returns normalized license number (uppercase, no spaces/dashes).
    """
    rule = LICENSE_REGION_BY_CODE.get(region_code)
    if not rule:
        raise ValidationError({'license_issuing_region': 'Select a valid province or state.'})

    normalized = normalize_license_number(license_number)
    if not normalized:
        raise ValidationError({'license_number': 'Driver license number is required.'})

    compiled = _COMPILED_REGION_PATTERNS[region_code]
    if not any(pattern.fullmatch(normalized) for pattern in compiled):
        raise ValidationError({
            'license_number': (
                f'Invalid {rule.name} driver license format. Expected: {rule.hint}.'
            ),
        })

    return normalized
