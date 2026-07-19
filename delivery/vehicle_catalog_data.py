"""Reference data for North American pickup truck catalog (1999–present).

Approximate factory max payload/towing ratings from manufacturer spec sheets.
Values are fleet-wide ceilings for validation — actual capacity varies by trim.
"""

from __future__ import annotations

from typing import TypedDict


class CatalogEntry(TypedDict):
    manufacturer: str
    model: str
    start_year: int
    end_year: int | None
    max_payload_lb: int
    max_towing_lb: int
    notes: str


# (manufacturer, model, start_year, end_year, max_payload_lb, max_towing_lb, notes)
VEHICLE_CATALOG_ENTRIES: tuple[CatalogEntry, ...] = (
    {'manufacturer': 'Ford', 'model': 'Ranger', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 1800, 'max_towing_lb': 7500, 'notes': 'Mid-size'},
    {'manufacturer': 'Ford', 'model': 'F-150', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 3325, 'max_towing_lb': 14000, 'notes': 'Most common delivery pickup'},
    {'manufacturer': 'Ford', 'model': 'F-250 Super Duty', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 4300, 'max_towing_lb': 23000, 'notes': 'Heavy-duty'},
    {'manufacturer': 'Ford', 'model': 'F-350 Super Duty', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 7850, 'max_towing_lb': 37000, 'notes': 'Heavy-duty'},
    {'manufacturer': 'Chevrolet', 'model': 'Colorado', 'start_year': 2004, 'end_year': None, 'max_payload_lb': 1684, 'max_towing_lb': 7700, 'notes': 'Mid-size'},
    {'manufacturer': 'Chevrolet', 'model': 'Silverado 1500', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 2260, 'max_towing_lb': 13300, 'notes': 'Full-size'},
    {'manufacturer': 'Chevrolet', 'model': 'Silverado 2500HD', 'start_year': 2001, 'end_year': None, 'max_payload_lb': 3979, 'max_towing_lb': 22500, 'notes': 'Heavy-duty'},
    {'manufacturer': 'Chevrolet', 'model': 'Silverado 3500HD', 'start_year': 2001, 'end_year': None, 'max_payload_lb': 7442, 'max_towing_lb': 36000, 'notes': 'Heavy-duty'},
    {'manufacturer': 'GMC', 'model': 'Canyon', 'start_year': 2004, 'end_year': None, 'max_payload_lb': 1684, 'max_towing_lb': 7700, 'notes': 'Colorado twin'},
    {'manufacturer': 'GMC', 'model': 'Sierra 1500', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 2240, 'max_towing_lb': 13300, 'notes': 'Full-size'},
    {'manufacturer': 'GMC', 'model': 'Sierra 2500HD', 'start_year': 2001, 'end_year': None, 'max_payload_lb': 3900, 'max_towing_lb': 22500, 'notes': 'Heavy-duty'},
    {'manufacturer': 'GMC', 'model': 'Sierra 3500HD', 'start_year': 2001, 'end_year': None, 'max_payload_lb': 7290, 'max_towing_lb': 36000, 'notes': 'Heavy-duty'},
    {'manufacturer': 'RAM', 'model': 'Dakota', 'start_year': 1999, 'end_year': 2011, 'max_payload_lb': 1900, 'max_towing_lb': 7250, 'notes': 'Mid-size'},
    {'manufacturer': 'RAM', 'model': '1500', 'start_year': 2011, 'end_year': None, 'max_payload_lb': 2300, 'max_towing_lb': 12750, 'notes': 'Full-size'},
    {'manufacturer': 'RAM', 'model': 'Ram 1500', 'start_year': 1999, 'end_year': 2010, 'max_payload_lb': 1900, 'max_towing_lb': 9100, 'notes': 'Before Ram became its own brand'},
    {'manufacturer': 'RAM', 'model': 'Ram 2500', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 4000, 'max_towing_lb': 20000, 'notes': 'Heavy-duty'},
    {'manufacturer': 'RAM', 'model': 'Ram 3500', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 7680, 'max_towing_lb': 37090, 'notes': 'Heavy-duty'},
    {'manufacturer': 'Toyota', 'model': 'Tacoma', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 1705, 'max_towing_lb': 6800, 'notes': 'Mid-size'},
    {'manufacturer': 'Toyota', 'model': 'Tundra', 'start_year': 2000, 'end_year': None, 'max_payload_lb': 1940, 'max_towing_lb': 12000, 'notes': 'Full-size'},
    {'manufacturer': 'Nissan', 'model': 'Frontier', 'start_year': 1999, 'end_year': None, 'max_payload_lb': 1620, 'max_towing_lb': 7150, 'notes': 'Mid-size'},
    {'manufacturer': 'Nissan', 'model': 'Titan', 'start_year': 2004, 'end_year': None, 'max_payload_lb': 1710, 'max_towing_lb': 11050, 'notes': 'Full-size'},
    {'manufacturer': 'Nissan', 'model': 'Titan XD', 'start_year': 2016, 'end_year': 2024, 'max_payload_lb': 2406, 'max_towing_lb': 12830, 'notes': 'Heavy-duty light pickup'},
    {'manufacturer': 'Honda', 'model': 'Ridgeline', 'start_year': 2006, 'end_year': None, 'max_payload_lb': 1583, 'max_towing_lb': 5000, 'notes': 'Unibody pickup'},
    {'manufacturer': 'Jeep', 'model': 'Gladiator', 'start_year': 2020, 'end_year': None, 'max_payload_lb': 1725, 'max_towing_lb': 7700, 'notes': 'Mid-size'},
    {'manufacturer': 'Rivian', 'model': 'R1T', 'start_year': 2022, 'end_year': None, 'max_payload_lb': 1764, 'max_towing_lb': 11000, 'notes': 'Electric'},
    {'manufacturer': 'Tesla', 'model': 'Cybertruck', 'start_year': 2023, 'end_year': None, 'max_payload_lb': 2500, 'max_towing_lb': 11000, 'notes': 'Electric'},
)
