"""Customer self-service profile via /customers/me/."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from delivery.models import Customer, Delivery


class CustomerMeAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cust.me',
            email='cust.me@example.com',
            password='TestPass1234!',
            first_name='Casey',
            last_name='Customer',
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='6045550100',
            address_street='123 Main St',
            address_city='Vancouver',
            address_state='BC',
            address_postal_code='V6B1A1',
            address_country='CA',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_customer_me(self):
        response = self.client.get('/api/customers/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '6045550100')

    def test_patch_customer_me(self):
        response = self.client.patch('/api/customers/me/', {
            'phone_number': '6045550199',
            'address_city': 'Burnaby',
            'preferred_pickup_address': 'Rear loading dock',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.phone_number, '6045550199')
        self.assertEqual(self.customer.address_city, 'Burnaby')
        self.assertEqual(self.customer.preferred_pickup_address, 'Rear loading dock')


class DeliveryCancelAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cancel.customer',
            email='cancel@example.com',
            password='TestPass1234!',
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='6045550101',
        )
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            pickup_location='A',
            dropoff_location='B',
            item_description='Boxes',
            status='Pending',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_customer_cancel_pending_delivery(self):
        response = self.client.post(f'/api/deliveries/{self.delivery.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'Cancelled')

    def test_customer_cannot_cancel_en_route_delivery(self):
        self.delivery.status = 'En Route'
        self.delivery.save(update_fields=['status'])
        response = self.client.post(f'/api/deliveries/{self.delivery.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
