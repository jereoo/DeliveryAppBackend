"""Tests for registration_service SSOT."""

from django.contrib.auth.models import User
from django.test import TestCase

from delivery.models import Customer
from delivery.registration_service import create_customer_as_staff, register_customer


class RegistrationServiceTests(TestCase):
    def test_register_customer_creates_non_staff_user(self):
        customer = register_customer({
            'user': {
                'username': 'regcust',
                'email': 'regcust@example.com',
                'password': 'testpass123',
                'first_name': 'Reg',
                'last_name': 'Customer',
            },
            'phone_number': '5551234567',
            'address_country': 'US',
        })
        self.assertEqual(customer.user.username, 'regcust')
        self.assertFalse(customer.user.is_staff)
        self.assertTrue(customer.user.is_active)
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())

    def test_create_customer_as_staff(self):
        customer = create_customer_as_staff({
            'user': {
                'username': 'admincust',
                'email': 'admincust@example.com',
                'password': 'testpass123',
                'first_name': 'Admin',
                'last_name': 'Created',
            },
            'phone_number': '5557654321',
            'address_country': 'US',
        })
        self.assertFalse(customer.user.is_staff)
        self.assertEqual(User.objects.filter(username='admincust').count(), 1)
