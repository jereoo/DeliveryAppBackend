# Demo / seed data tests — Phase 2

import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from delivery.models import Customer, Delivery, Driver, Vehicle
from delivery.seed_demo import DEMO_CUSTOMER_USERNAME, DEMO_DRIVER_USERNAME, seed_demo_data


class SeedDemoDataTests(TestCase):
    def test_seed_demo_data_creates_known_accounts(self):
        result = seed_demo_data()
        self.assertFalse(result['skipped'])
        self.assertTrue(User.objects.filter(username=DEMO_DRIVER_USERNAME).exists())
        self.assertTrue(User.objects.filter(username=DEMO_CUSTOMER_USERNAME).exists())
        self.assertTrue(Driver.objects.filter(license_number='DL-DEMO-001').exists())
        self.assertTrue(Vehicle.objects.filter(license_plate='DEMO001').exists())
        self.assertEqual(Delivery.objects.filter(customer__user__username=DEMO_CUSTOMER_USERNAME).count(), 1)

    def test_seed_demo_data_skips_when_demo_driver_exists(self):
        seed_demo_data()
        result = seed_demo_data()
        self.assertTrue(result['skipped'])

    def test_seed_demo_data_force_replaces_demo_rows(self):
        seed_demo_data()
        Customer.objects.filter(user__username=DEMO_CUSTOMER_USERNAME).update(phone_number='5550000000')
        seed_demo_data(force=True)
        customer = Customer.objects.get(user__username=DEMO_CUSTOMER_USERNAME)
        self.assertEqual(customer.phone_number, '5550100200')

    def test_management_command_if_empty_skips(self):
        Driver.objects.create(
            user=User.objects.create_user(username='other.driver', password='x'),
            first_name='Other',
            last_name='Driver',
            phone_number='555',
            license_number='DL-OTHER-1',
        )
        out = call_command('seed_demo_data', '--if-empty')
        self.assertFalse(User.objects.filter(username=DEMO_DRIVER_USERNAME).exists())

    @patch.dict(os.environ, {'DYNO': 'web.1'}, clear=False)
    def test_management_command_blocks_heroku_without_flag(self):
        with self.assertRaises(CommandError):
            call_command('seed_demo_data')
