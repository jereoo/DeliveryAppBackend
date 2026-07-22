"""Idempotent demo/staging seed data — single source of truth for Phase 2+."""
from __future__ import annotations

from datetime import date

from django.contrib.auth.models import User
from django.db import transaction

from delivery.models import Customer, Delivery, Driver, DriverApprovalStatus, DriverVehicle, LegalDocument, Vehicle
from delivery.seed_helpers import (
    assign_vehicle_to_driver,
    clear_legal_documents,
    ensure_user_account,
    get_or_create_seed_staff,
    seed_compliance_documents,
    upsert_catalog_vehicle,
    upsert_driver,
)

DEMO_DRIVER_USERNAME = 'demo.driver'
DEMO_CUSTOMER_USERNAME = 'demo.customer'
DEMO_DRIVER_PASSWORD = 'DemoPass1234!'
DEMO_CUSTOMER_PASSWORD = 'DemoPass1234!'

# CA-ON format (ServiceOntario): 1 letter + 14 digits
DEMO_DRIVER_LICENSE = 'D88887777666666'
DEMO_DRIVER_LICENSE_REGION = 'CA-ON'
DEMO_VEHICLE_PLATE = 'DEMO001'
DEMO_VEHICLE_VIN = '1DEMOVIN00000001'
DEMO_VEHICLE_MANUFACTURER = 'Ford'
DEMO_VEHICLE_MODEL = 'F-150'
DEMO_VEHICLE_YEAR = 2022
DEMO_VEHICLE_CAPACITY_KG = 1200

DEMO_DELIVERY_PICKUP = '100 Demo Street, Toronto, ON M5H 2N2, Canada'
DEMO_DELIVERY_DROPOFF = '200 Sample Ave, Toronto, ON M5B 1B1, Canada'
DEMO_DELIVERY_DESCRIPTION = 'Demo delivery — office chair'


class DemoSeedError(Exception):
    pass


def demo_users_exist() -> bool:
    return User.objects.filter(username__in=[DEMO_DRIVER_USERNAME, DEMO_CUSTOMER_USERNAME]).exists()


def any_fleet_data_exists() -> bool:
    return Driver.objects.exists() or Customer.objects.count() > 1


@transaction.atomic
def seed_demo_data(*, force: bool = False) -> dict:
    """
    Create a small known demo dataset for dev/staging QA.
    Returns counts of created/skipped entities.
    """
    if not force and Driver.objects.filter(user__username=DEMO_DRIVER_USERNAME).exists():
        return {'skipped': True, 'reason': 'demo.driver already exists'}

    if force:
        _clear_demo_rows()

    staff = get_or_create_seed_staff()

    driver_user, driver_created = ensure_user_account(
        username=DEMO_DRIVER_USERNAME,
        email='demo.driver@example.com',
        password=DEMO_DRIVER_PASSWORD,
        first_name='Demo',
        last_name='Driver',
        force_password=force,
    )

    customer_user, customer_created = ensure_user_account(
        username=DEMO_CUSTOMER_USERNAME,
        email='demo.customer@example.com',
        password=DEMO_CUSTOMER_PASSWORD,
        first_name='Demo',
        last_name='Customer',
        force_password=force,
    )

    driver, _ = upsert_driver(
        user=driver_user,
        staff=staff,
        first_name='Demo',
        last_name='Driver',
        phone_number='5550100100',
        license_number=DEMO_DRIVER_LICENSE,
        license_issuing_region=DEMO_DRIVER_LICENSE_REGION,
        approval_status=DriverApprovalStatus.APPROVED,
        active=True,
    )

    customer, _ = Customer.objects.update_or_create(
        user=customer_user,
        defaults={
            'phone_number': '5550100200',
            'address_street': '100 Demo Street',
            'address_city': 'Toronto',
            'address_state': 'ON',
            'address_postal_code': 'M5H 2N2',
            'address_country': 'CA',
            'is_business': False,
            'active': True,
        },
    )

    vehicle, vehicle_created = upsert_catalog_vehicle(
        license_plate=DEMO_VEHICLE_PLATE,
        manufacturer=DEMO_VEHICLE_MANUFACTURER,
        model=DEMO_VEHICLE_MODEL,
        year=DEMO_VEHICLE_YEAR,
        vin=DEMO_VEHICLE_VIN,
        capacity_kg=DEMO_VEHICLE_CAPACITY_KG,
        active=True,
    )

    assign_vehicle_to_driver(driver, vehicle)

    legal_documents = seed_compliance_documents(
        staff,
        driver,
        vehicle,
        'full_verified',
    )

    delivery, delivery_created = Delivery.objects.get_or_create(
        customer=customer,
        pickup_location=DEMO_DELIVERY_PICKUP,
        dropoff_location=DEMO_DELIVERY_DROPOFF,
        item_description=DEMO_DELIVERY_DESCRIPTION,
        defaults={
            'status': 'Pending',
            'same_pickup_as_customer': False,
            'use_preferred_pickup': False,
            'same_dropoff_as_customer': False,
        },
    )

    return {
        'skipped': False,
        'driver_created': driver_created,
        'customer_created': customer_created,
        'vehicle_created': vehicle_created,
        'delivery_created': delivery_created,
        'legal_documents': legal_documents,
        'driver_username': DEMO_DRIVER_USERNAME,
        'customer_username': DEMO_CUSTOMER_USERNAME,
        'vehicle_plate': vehicle.license_plate,
        'delivery_id': delivery.id,
        'driver_license_region': driver.license_issuing_region,
        'vehicle_model_spec_id': vehicle.model_spec_id,
    }


def _clear_demo_rows():
    """Remove demo users and linked rows (not staff/admin)."""
    demo_users = User.objects.filter(username__in=[DEMO_DRIVER_USERNAME, DEMO_CUSTOMER_USERNAME])
    driver_ids = list(Driver.objects.filter(user__in=demo_users).values_list('id', flat=True))
    customer_ids = list(Customer.objects.filter(user__in=demo_users).values_list('id', flat=True))

    if customer_ids:
        Delivery.objects.filter(customer_id__in=customer_ids).delete()
    if driver_ids:
        LegalDocument.objects.filter(driver_id__in=driver_ids).delete()
        DriverVehicle.objects.filter(driver_id__in=driver_ids).delete()
        Driver.objects.filter(id__in=driver_ids).delete()
    if customer_ids:
        Customer.objects.filter(id__in=customer_ids).delete()

    vehicle = Vehicle.objects.filter(license_plate=DEMO_VEHICLE_PLATE).first()
    if vehicle:
        clear_legal_documents(vehicle=vehicle)
        vehicle.delete()

    demo_users.delete()
