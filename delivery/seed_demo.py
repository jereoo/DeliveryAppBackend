"""Idempotent demo/staging seed data — single source of truth for Phase 2."""
from datetime import date

from django.contrib.auth.models import User
from django.db import transaction

from delivery.models import Customer, Delivery, Driver, DriverVehicle, Vehicle

DEMO_DRIVER_USERNAME = 'demo.driver'
DEMO_CUSTOMER_USERNAME = 'demo.customer'
DEMO_DRIVER_PASSWORD = 'DemoPass1234!'
DEMO_CUSTOMER_PASSWORD = 'DemoPass1234!'

DEMO_DRIVER_LICENSE = 'DL-DEMO-001'
DEMO_VEHICLE_PLATE = 'DEMO001'
DEMO_VEHICLE_VIN = '1DEMOVIN00000001'


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

    driver_user, driver_created = User.objects.get_or_create(
        username=DEMO_DRIVER_USERNAME,
        defaults={
            'email': 'demo.driver@example.com',
            'first_name': 'Demo',
            'last_name': 'Driver',
        },
    )
    if driver_created or force:
        driver_user.set_password(DEMO_DRIVER_PASSWORD)
        driver_user.save()

    customer_user, customer_created = User.objects.get_or_create(
        username=DEMO_CUSTOMER_USERNAME,
        defaults={
            'email': 'demo.customer@example.com',
            'first_name': 'Demo',
            'last_name': 'Customer',
        },
    )
    if customer_created or force:
        customer_user.set_password(DEMO_CUSTOMER_PASSWORD)
        customer_user.save()

    driver, _ = Driver.objects.update_or_create(
        user=driver_user,
        defaults={
            'first_name': 'Demo',
            'last_name': 'Driver',
            'phone_number': '5550100100',
            'license_number': DEMO_DRIVER_LICENSE,
            'active': True,
        },
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

    vehicle, _ = Vehicle.objects.update_or_create(
        license_plate=DEMO_VEHICLE_PLATE,
        defaults={
            'make': 'Ford',
            'model': 'Transit',
            'year': 2022,
            'vin': DEMO_VEHICLE_VIN,
            'capacity': 1500,
            'capacity_unit': 'kg',
            'active': True,
        },
    )

    DriverVehicle.objects.update_or_create(
        driver=driver,
        vehicle=vehicle,
        assigned_from=date.today(),
        defaults={'assigned_to': None},
    )

    delivery, delivery_created = Delivery.objects.get_or_create(
        customer=customer,
        pickup_location='100 Demo Street, Toronto, ON M5H 2N2, Canada',
        dropoff_location='200 Sample Ave, Toronto, ON M5B 1B1, Canada',
        item_description='Demo delivery — office chair',
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
        'delivery_created': delivery_created,
        'driver_username': DEMO_DRIVER_USERNAME,
        'customer_username': DEMO_CUSTOMER_USERNAME,
        'vehicle_plate': vehicle.license_plate,
        'delivery_id': delivery.id,
    }


def _clear_demo_rows():
    """Remove demo users and linked rows (not staff/admin)."""
    demo_users = User.objects.filter(username__in=[DEMO_DRIVER_USERNAME, DEMO_CUSTOMER_USERNAME])
    driver_ids = list(Driver.objects.filter(user__in=demo_users).values_list('id', flat=True))
    customer_ids = list(Customer.objects.filter(user__in=demo_users).values_list('id', flat=True))

    if customer_ids:
        Delivery.objects.filter(customer_id__in=customer_ids).delete()
    if driver_ids:
        DriverVehicle.objects.filter(driver_id__in=driver_ids).delete()
        Driver.objects.filter(id__in=driver_ids).delete()
    if customer_ids:
        Customer.objects.filter(id__in=customer_ids).delete()
    Vehicle.objects.filter(license_plate=DEMO_VEHICLE_PLATE).delete()
    demo_users.delete()
