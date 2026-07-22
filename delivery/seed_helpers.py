"""Shared helpers for demo and test seed commands."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from django.contrib.auth.models import User
from django.utils import timezone

from delivery.compliance_constants import CoverageType, DocumentType
from delivery.compliance_service import create_document, mark_verified
from delivery.models import Driver, DriverApprovalStatus, DriverVehicle, LegalDocument, Vehicle, VehicleModelSpec

SEED_STAFF_USERNAME = 'seed.staff'

DocScenario = Literal['full_verified', 'pending', 'partial', 'none']


def get_or_create_seed_staff() -> User:
    staff = User.objects.filter(is_staff=True).order_by('id').first()
    if staff:
        return staff

    staff, created = User.objects.get_or_create(
        username=SEED_STAFF_USERNAME,
        defaults={
            'email': 'seed.staff@example.com',
            'is_staff': True,
            'is_superuser': True,
        },
    )
    if created:
        staff.set_password('SeedStaff1234!')
        staff.save()
    return staff


def get_model_spec(manufacturer: str, model: str) -> VehicleModelSpec:
    return VehicleModelSpec.objects.select_related('manufacturer').get(
        manufacturer__name=manufacturer,
        name=model,
        is_active=True,
    )


def ensure_user_account(
    *,
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    force_password: bool = False,
) -> tuple[User, bool]:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        },
    )
    if created or force_password or not user.has_usable_password():
        user.set_password(password)
        user.save(update_fields=['password'])
    return user, created


def upsert_catalog_vehicle(
    *,
    license_plate: str,
    manufacturer: str,
    model: str,
    year: int,
    vin: str,
    capacity_kg: int,
    active: bool = True,
) -> tuple[Vehicle, bool]:
    spec = get_model_spec(manufacturer, model)
    return Vehicle.objects.update_or_create(
        license_plate=license_plate,
        defaults={
            'model_spec': spec,
            'make': spec.manufacturer.name,
            'model': spec.name,
            'year': year,
            'vin': vin,
            'capacity': capacity_kg,
            'capacity_unit': 'kg',
            'active': active,
        },
    )


def upsert_driver(
    *,
    user: User,
    staff: User,
    first_name: str,
    last_name: str,
    phone_number: str,
    license_number: str,
    license_issuing_region: str,
    approval_status: str = DriverApprovalStatus.APPROVED,
    active: bool = True,
    rejection_reason: str = '',
) -> tuple[Driver, bool]:
    approved_at = timezone.now() if approval_status == DriverApprovalStatus.APPROVED else None
    approved_by = staff if approval_status == DriverApprovalStatus.APPROVED else None

    return Driver.objects.update_or_create(
        user=user,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'license_number': license_number,
            'license_issuing_region': license_issuing_region,
            'active': active,
            'approval_status': approval_status,
            'approval_rejection_reason': rejection_reason or None,
            'approved_at': approved_at,
            'approved_by': approved_by,
        },
    )


def assign_vehicle_to_driver(driver: Driver, vehicle: Vehicle, assigned_from: date | None = None) -> DriverVehicle:
    assigned_from = assigned_from or date.today()
    assignment, _ = DriverVehicle.objects.update_or_create(
        driver=driver,
        vehicle=vehicle,
        assigned_from=assigned_from,
        defaults={'assigned_to': None},
    )
    return assignment


def clear_legal_documents(*, driver: Driver | None = None, vehicle: Vehicle | None = None) -> int:
    qs = LegalDocument.objects.all()
    if driver is not None:
        qs = qs.filter(driver=driver)
    if vehicle is not None:
        qs = qs.filter(vehicle=vehicle)
    count, _ = qs.delete()
    return count


def seed_compliance_documents(
    staff: User,
    driver: Driver,
    vehicle: Vehicle,
    scenario: DocScenario,
    *,
    days: int = 90,
) -> int:
    """Create legal documents for a driver/vehicle pair. Returns document count."""
    clear_legal_documents(driver=driver, vehicle=vehicle)

    if scenario == 'none':
        return 0

    expiry = date.today() + timedelta(days=days)
    effective = date.today() - timedelta(days=30)
    created = 0

    if scenario in ('full_verified', 'partial'):
        license_doc = create_document(
            staff,
            driver=driver,
            data={
                'document_type': DocumentType.DRIVER_LICENSE,
                'issuer': 'ServiceOntario' if driver.license_issuing_region == 'CA-ON' else (
                    'ICBC' if driver.license_issuing_region.startswith('CA-') else 'DMV'
                ),
                'effective_date': effective,
                'expiry_date': expiry,
            },
        )
        mark_verified(staff, license_doc.id)
        created += 1

    if scenario == 'pending':
        create_document(
            staff,
            driver=driver,
            data={
                'document_type': DocumentType.DRIVER_LICENSE,
                'issuer': 'ServiceOntario',
                'effective_date': effective,
                'expiry_date': expiry,
            },
        )
        create_document(
            staff,
            vehicle=vehicle,
            data={
                'document_type': DocumentType.VEHICLE_REGISTRATION,
                'effective_date': effective,
                'expiry_date': expiry,
            },
        )
        create_document(
            staff,
            vehicle=vehicle,
            data={
                'document_type': DocumentType.COMMERCIAL_INSURANCE,
                'coverage_type': CoverageType.COMMERCIAL,
                'policy_number': f'POL-PENDING-{vehicle.license_plate}',
                'issuer': 'Demo Insurance Co.',
                'effective_date': effective,
                'expiry_date': expiry,
            },
        )
        return 3

    if scenario in ('full_verified', 'partial'):
        for doc_type in (DocumentType.VEHICLE_REGISTRATION, DocumentType.COMMERCIAL_INSURANCE):
            data = {
                'document_type': doc_type,
                'effective_date': effective,
                'expiry_date': expiry,
            }
            if doc_type == DocumentType.COMMERCIAL_INSURANCE:
                data.update(
                    coverage_type=CoverageType.COMMERCIAL,
                    policy_number=f'POL-{vehicle.license_plate}',
                    issuer='Demo Insurance Co.',
                )
            doc = create_document(staff, vehicle=vehicle, data=data)
            if scenario == 'full_verified':
                mark_verified(staff, doc.id)
            created += 1

    return created
