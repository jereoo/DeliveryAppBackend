"""Phase 4G Slice 5 — staff audit log and invite-by-email."""

from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import StaffAuditEvent, StaffInvite, StaffProfile
from delivery.staff_constants import StaffAuditEventType, StaffRole


class StaffSlice5Tests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='testpass123',
            email='super@example.com',
            is_staff=True,
            is_superuser=True,
        )
        StaffProfile.objects.create(
            user=self.super_admin,
            staff_role=StaffRole.SUPER_ADMIN,
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    @override_settings(STAFF_INVITE_WEB_BASE_URL='https://www.buynhaul.com')
    def test_create_staff_writes_audit_event(self):
        self._auth(self.super_admin)
        response = self.client.post(
            '/api/staff/',
            {
                'username': 'newstaff',
                'email': 'newstaff@example.com',
                'password': 'SecurePass1!',
                'first_name': 'New',
                'last_name': 'Staff',
                'staff_role': StaffRole.READ_ONLY,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        events = StaffAuditEvent.objects.filter(event_type=StaffAuditEventType.STAFF_CREATED)
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().actor_id, self.super_admin.id)

    def test_role_change_writes_audit_event(self):
        target_user = User.objects.create_user(
            username='targetstaff',
            password='testpass123',
            email='target@example.com',
            is_staff=True,
        )
        profile = StaffProfile.objects.create(
            user=target_user,
            staff_role=StaffRole.READ_ONLY,
        )
        self._auth(self.super_admin)
        response = self.client.patch(
            f'/api/staff/{profile.id}/',
            {'staff_role': StaffRole.COMPLIANCE_REVIEWER},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event = StaffAuditEvent.objects.filter(
            event_type=StaffAuditEventType.ROLE_CHANGED,
            target_profile=profile,
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.old_role, StaffRole.READ_ONLY)
        self.assertEqual(event.new_role, StaffRole.COMPLIANCE_REVIEWER)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        STAFF_INVITE_WEB_BASE_URL='https://www.buynhaul.com',
    )
    def test_invite_flow_creates_audit_and_accepts(self):
        self._auth(self.super_admin)
        mail.outbox.clear()
        create = self.client.post(
            '/api/staff-invites/',
            {
                'email': 'invited@example.com',
                'staff_role': StaffRole.OPERATIONS_ADMIN,
                'first_name': 'Inv',
                'last_name': 'Ited',
            },
            format='json',
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('staff_invite=', mail.outbox[0].body)

        invite = StaffInvite.objects.get(email='invited@example.com')
        self.assertTrue(
            StaffAuditEvent.objects.filter(
                event_type=StaffAuditEventType.INVITE_SENT,
                target_email='invited@example.com',
            ).exists()
        )

        self.client.credentials()
        validate = self.client.get(f'/api/staff-invites/public/?token={invite.token}')
        self.assertEqual(validate.status_code, status.HTTP_200_OK)
        self.assertTrue(validate.data['valid'])

        accept = self.client.post(
            '/api/staff-invites/public/',
            {
                'token': invite.token,
                'username': 'inviteduser',
                'password': 'SecurePass1!',
            },
            format='json',
        )
        self.assertEqual(accept.status_code, status.HTTP_201_CREATED)
        profile = StaffProfile.objects.get(user__username='inviteduser')
        self.assertEqual(profile.staff_role, StaffRole.OPERATIONS_ADMIN)
        invite.refresh_from_db()
        self.assertIsNotNone(invite.accepted_at)

    def test_super_admin_can_list_audit_events(self):
        StaffAuditEvent.objects.create(
            actor=self.super_admin,
            event_type=StaffAuditEventType.INVITE_SENT,
            target_email='x@example.com',
            new_role=StaffRole.READ_ONLY,
        )
        self._auth(self.super_admin)
        response = self.client.get('/api/staff-audit-events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
