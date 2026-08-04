"""Customer and driver registration workflows (SSOT for profile creation)."""

from django.contrib.auth.models import User

from .models import Customer, Driver, DriverApprovalStatus, VehicleApprovalStatus
from .vehicle_onboarding_service import assign_vehicle_to_driver, create_vehicle_from_catalog


def create_customer_user(user_data: dict, *, is_active: bool = True) -> User:
    """Create a non-staff User for a customer profile."""
    return User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data.get('first_name', ''),
        last_name=user_data.get('last_name', ''),
        is_active=is_active,
        is_staff=False,
        is_superuser=False,
    )


def register_customer(validated_data: dict) -> Customer:
    """Public self-registration: User + Customer."""
    user_data = validated_data.pop('user')
    user = create_customer_user(user_data, is_active=True)
    customer = Customer(**validated_data)
    customer.user = user
    customer.save(validate=False)
    return customer


def create_customer_as_staff(validated_data: dict) -> Customer:
    """Admin creates customer via CustomerSerializer."""
    user_data = validated_data.pop('user')
    user = create_customer_user(user_data, is_active=True)
    return Customer.objects.create(user=user, **validated_data)


def create_driver_as_staff(validated_data: dict) -> Driver:
    """Admin creates driver with User account; auto-approved when active."""
    username = validated_data.pop('username')
    email = validated_data.pop('email')
    password = validated_data.pop('password')
    first_name = validated_data.pop('first_name')
    last_name = validated_data.pop('last_name')
    active = validated_data.pop('active', True)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=False,
        is_superuser=False,
    )

    return Driver.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        active=active,
        approval_status=DriverApprovalStatus.APPROVED if active else DriverApprovalStatus.PENDING,
        **validated_data,
    )


def register_driver(validated_data: dict) -> Driver:
    """Driver self-registration: User + Driver + catalog vehicle assignment."""
    validated_data.pop('full_name', None)
    user_data = validated_data.pop('user')
    vehicle_year = validated_data.pop('vehicle_year')
    validated_data.pop('_vehicle_model_spec', None)
    spec_id = validated_data.pop('vehicle_model_spec_id')

    vehicle = create_vehicle_from_catalog(
        vehicle_model_spec_id=spec_id,
        vehicle_year=vehicle_year,
        vehicle_license_plate=validated_data.pop('vehicle_license_plate'),
        vehicle_vin=validated_data.pop('vehicle_vin'),
        vehicle_capacity=validated_data.pop('vehicle_capacity'),
        vehicle_capacity_unit=validated_data.pop('vehicle_capacity_unit'),
        approval_status=VehicleApprovalStatus.PENDING,
        active=False,
    )

    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        is_staff=False,
        is_superuser=False,
    )

    validated_data['first_name'] = user_data['first_name']
    validated_data['last_name'] = user_data['last_name']
    license_issuing_region = validated_data.pop('license_issuing_region')

    driver = Driver.objects.create(
        user=user,
        **validated_data,
        license_issuing_region=license_issuing_region,
        active=False,
        approval_status=DriverApprovalStatus.PENDING,
    )
    assign_vehicle_to_driver(driver, vehicle)
    return driver
