"""One-shot: ensure admin user exists for production (Heroku). Usage: python manage.py ensure_admin"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update admin / admin123 (staff + superuser)'

    def handle(self, *args, **options):
        u, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
        )
        u.set_password('admin123')
        u.is_staff = True
        u.is_superuser = True
        u.email = u.email or 'admin@example.com'
        u.save()
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'} user admin"))
