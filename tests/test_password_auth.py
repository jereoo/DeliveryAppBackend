"""Password change, reset, and staff temp password."""

from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import StaffProfile
from delivery.staff_constants import StaffRole


class PasswordAuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='OldPass123!',
            email='super@example.com',
            is_staff=True,
            is_superuser=True,
        )
        StaffProfile.objects.create(
            user=self.super_admin,
            staff_role=StaffRole.SUPER_ADMIN,
            must_change_password=True,
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_create_staff_without_password_emails_temp(self):
        self._auth(self.super_admin)
        mail.outbox.clear()
        response = self.client.post(
            '/api/staff/',
            {
                'username': 'tempstaff',
                'email': 'tempstaff@example.com',
                'first_name': 'Temp',
                'last_name': 'Staff',
                'staff_role': StaffRole.READ_ONLY,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        profile = StaffProfile.objects.get(user__username='tempstaff')
        self.assertTrue(profile.must_change_password)

    def test_me_includes_must_change_password(self):
        self._auth(self.super_admin)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['must_change_password'])

    def test_change_password_clears_flag(self):
        self._auth(self.super_admin)
        response = self.client.post(
            '/api/auth/password/change/',
            {
                'current_password': 'OldPass123!',
                'new_password': 'NewPass123!',
                'confirm_password': 'NewPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.super_admin.refresh_from_db()
        self.assertTrue(self.super_admin.check_password('NewPass123!'))
        me = self.client.get('/api/me/')
        self.assertFalse(me.data['must_change_password'])

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        STAFF_INVITE_WEB_BASE_URL='https://www.buynhaul.com',
    )
    def test_forgot_password_sends_email(self):
        mail.outbox.clear()
        response = self.client.post(
            '/api/auth/password/forgot/',
            {'email': 'super@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('password_reset=', mail.outbox[0].body)
