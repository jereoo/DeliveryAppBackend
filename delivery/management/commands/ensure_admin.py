"""Ensure a staff superuser exists. Password comes from env — never hardcoded."""
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        'Create or update the bootstrap admin user. '
        'Set ADMIN_PASSWORD (and optionally ADMIN_USERNAME, ADMIN_EMAIL). '
        'On Heroku: heroku config:set ADMIN_PASSWORD=... -a truck-buddy && '
        'heroku run python manage.py ensure_admin -a truck-buddy'
    )

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME', 'admin').strip()
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com').strip()
        password = os.environ.get('ADMIN_PASSWORD', '').strip()

        if not password:
            if getattr(settings, 'HEROKU', False) or not settings.DEBUG:
                raise CommandError(
                    'ADMIN_PASSWORD is required in production. '
                    'Set it in Heroku config or .env before running ensure_admin.'
                )
            raise CommandError(
                'ADMIN_PASSWORD is not set. Add it to .env for local bootstrap, e.g. '
                'ADMIN_PASSWORD=your-strong-password'
            )

        if len(password) < 12:
            raise CommandError('ADMIN_PASSWORD must be at least 12 characters.')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.email = email
        user.is_active = True  # JWT "No active account" if False
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        verb = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f"{verb} staff user '{username}' (password from ADMIN_PASSWORD)"))
