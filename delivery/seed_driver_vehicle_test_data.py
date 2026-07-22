"""Catalog-compliant driver, vehicle, and legal document test data for local QA."""
from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import User
from django.db import transaction

from delivery.models import Driver, DriverApprovalStatus, DriverVehicle, LegalDocument, Vehicle
from delivery.seed_helpers import (
    DocScenario,
    assign_vehicle_to_driver,
    ensure_user_account,
    get_or_create_seed_staff,
    seed_compliance_documents,
    upsert_catalog_vehicle,
    upsert_driver,
)

TEST_DRIVER_PASSWORD = 'TestPass1234!'


@dataclass(frozen=True)
class TestDriverProfile:
    username: str
    first_name: str
    last_name: str
    phone_number: str
    license_region: str
    license_number: str
    approval_status: str
    active: bool
    manufacturer: str
    model: str
    vehicle_year: int
    license_plate: str
    vin: str
    capacity_kg: int
    doc_scenario: DocScenario
    rejection_reason: str = ''


TEST_DRIVER_PROFILES: tuple[TestDriverProfile, ...] = (
    TestDriverProfile(
        username='test.driver.approved',
        first_name='Alex',
        last_name='Approved',
        phone_number='6045550101',
        license_region='CA-BC',
        license_number='1234567',
        approval_status=DriverApprovalStatus.APPROVED,
        active=True,
        manufacturer='Ford',
        model='F-150',
        vehicle_year=2022,
        license_plate='TEST001',
        vin='1TESTAPPROVED0001',
        capacity_kg=1200,
        doc_scenario='full_verified',
    ),
    TestDriverProfile(
        username='test.driver.pending',
        first_name='Maria',
        last_name='Pending',
        phone_number='4165550102',
        license_region='CA-ON',
        license_number='D12345678901234',
        approval_status=DriverApprovalStatus.PENDING,
        active=False,
        manufacturer='Chevrolet',
        model='Silverado 1500',
        vehicle_year=2021,
        license_plate='TEST002',
        vin='1TESTPENDING00002',
        capacity_kg=900,
        doc_scenario='pending',
    ),
    TestDriverProfile(
        username='test.driver.rejected',
        first_name='Sam',
        last_name='Rejected',
        phone_number='4155550103',
        license_region='US-CA',
        license_number='B1234567',
        approval_status=DriverApprovalStatus.REJECTED,
        active=False,
        manufacturer='Toyota',
        model='Tacoma',
        vehicle_year=2020,
        license_plate='TEST003',
        vin='1TESTREJECT000003',
        capacity_kg=750,
        doc_scenario='none',
        rejection_reason='Incomplete background check.',
    ),
    TestDriverProfile(
        username='test.driver.partial',
        first_name='Jordan',
        last_name='Partial',
        phone_number='6045550104',
        license_region='CA-BC',
        license_number='7654321',
        approval_status=DriverApprovalStatus.APPROVED,
        active=True,
        manufacturer='RAM',
        model='1500',
        vehicle_year=2023,
        license_plate='TEST004',
        vin='1TESTPARTIAL00004',
        capacity_kg=1000,
        doc_scenario='partial',
    ),
    TestDriverProfile(
        username='test.driver.inactive',
        first_name='Casey',
        last_name='Inactive',
        phone_number='6045550105',
        license_region='CA-BC',
        license_number='2468135',
        approval_status=DriverApprovalStatus.APPROVED,
        active=False,
        manufacturer='GMC',
        model='Sierra 1500',
        vehicle_year=2019,
        license_plate='TEST005',
        vin='1TESTINACTIVE0005',
        capacity_kg=850,
        doc_scenario='full_verified',
    ),
)


def get_test_driver_usernames() -> tuple[str, ...]:
    return tuple(profile.username for profile in TEST_DRIVER_PROFILES)


def clear_driver_vehicle_data() -> dict:
    """Remove all drivers, vehicles, assignments, and legal documents. Keeps customers/deliveries."""
    driver_user_ids = list(Driver.objects.values_list('user_id', flat=True))

    legal_docs = LegalDocument.objects.count()
    assignments = DriverVehicle.objects.count()
    drivers = Driver.objects.count()
    vehicles = Vehicle.objects.count()

    LegalDocument.objects.all().delete()
    DriverVehicle.objects.all().delete()
    Driver.objects.all().delete()
    Vehicle.objects.all().delete()

    users_removed = 0
    if driver_user_ids:
        users_removed, _ = User.objects.filter(
            id__in=driver_user_ids,
            is_superuser=False,
        ).delete()

    return {
        'legal_documents': legal_docs,
        'driver_vehicles': assignments,
        'drivers': drivers,
        'vehicles': vehicles,
        'driver_users': users_removed,
    }


def _create_profile(staff: User, profile: TestDriverProfile) -> dict:
    user, user_created = ensure_user_account(
        username=profile.username,
        email=f'{profile.username}@example.com',
        password=TEST_DRIVER_PASSWORD,
        first_name=profile.first_name,
        last_name=profile.last_name,
    )

    driver, driver_created = upsert_driver(
        user=user,
        staff=staff,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone_number=profile.phone_number,
        license_number=profile.license_number,
        license_issuing_region=profile.license_region,
        approval_status=profile.approval_status,
        active=profile.active,
        rejection_reason=profile.rejection_reason,
    )

    vehicle, vehicle_created = upsert_catalog_vehicle(
        license_plate=profile.license_plate,
        manufacturer=profile.manufacturer,
        model=profile.model,
        year=profile.vehicle_year,
        vin=profile.vin,
        capacity_kg=profile.capacity_kg,
        active=profile.active,
    )

    assign_vehicle_to_driver(driver, vehicle)

    doc_count = seed_compliance_documents(
        staff,
        driver,
        vehicle,
        profile.doc_scenario,
    )

    return {
        'username': profile.username,
        'driver_id': driver.id,
        'vehicle_id': vehicle.id,
        'vehicle_plate': vehicle.license_plate,
        'user_created': user_created,
        'driver_created': driver_created,
        'vehicle_created': vehicle_created,
        'legal_documents': doc_count,
        'approval_status': profile.approval_status,
        'doc_scenario': profile.doc_scenario,
    }


@transaction.atomic
def seed_driver_vehicle_test_data(*, force: bool = False) -> dict:
    """
    Replace driver/vehicle/legal-document rows with catalog-compliant test profiles.
    Does not touch customers, deliveries, or delivery assignments.
    """
    if not force:
        if Driver.objects.filter(user__username__in=get_test_driver_usernames()).exists():
            return {'skipped': True, 'reason': 'test.driver.* profiles already exist (use --force)'}
        if Driver.objects.exists():
            return {
                'skipped': True,
                'reason': 'other driver data exists — run with --force to replace all driver/vehicle rows',
            }

    cleared = clear_driver_vehicle_data() if force or Driver.objects.exists() else {
        'legal_documents': 0,
        'driver_vehicles': 0,
        'drivers': 0,
        'vehicles': 0,
        'driver_users': 0,
    }

    staff = get_or_create_seed_staff()
    profiles = [_create_profile(staff, profile) for profile in TEST_DRIVER_PROFILES]

    return {
        'skipped': False,
        'cleared': cleared,
        'profiles': profiles,
        'password': TEST_DRIVER_PASSWORD,
        'staff_username': staff.username,
    }
