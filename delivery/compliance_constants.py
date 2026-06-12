"""Legal document enums — shared by models, services, serializers."""

from django.db import models


class DocumentType(models.TextChoices):
    DRIVER_LICENSE = 'DRIVER_LICENSE', 'Driver license'
    VEHICLE_REGISTRATION = 'VEHICLE_REGISTRATION', 'Vehicle registration'
    COMMERCIAL_INSURANCE = 'COMMERCIAL_INSURANCE', 'Commercial insurance'
    INSPECTION = 'INSPECTION', 'Inspection'


class DocumentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'
    EXPIRED = 'EXPIRED', 'Expired'


class CoverageType(models.TextChoices):
    COMMERCIAL = 'COMMERCIAL', 'Commercial'
    PERSONAL = 'PERSONAL', 'Personal'
    OTHER = 'OTHER', 'Other'


DRIVER_DOCUMENT_TYPES = frozenset({DocumentType.DRIVER_LICENSE})

VEHICLE_DOCUMENT_TYPES = frozenset({
    DocumentType.VEHICLE_REGISTRATION,
    DocumentType.COMMERCIAL_INSURANCE,
    DocumentType.INSPECTION,
})
