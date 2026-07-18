"""Reject driver-license records that are likely misclassified vehicle/insurance uploads."""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from delivery.compliance_service import (
    find_misclassified_driver_documents,
    reject_misclassified_driver_documents,
)


class Command(BaseCommand):
    help = (
        'Find driver-license documents that look like registration/insurance uploads '
        'stored on the driver record before the compliance UI fix. '
        'Dry-run by default; pass --apply to reject them.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Reject matching documents (default is dry-run list only)',
        )
        parser.add_argument(
            '--staff-username',
            default='',
            help='Staff user for reject audit trail (default: first is_staff user)',
        )
        parser.add_argument(
            '--reason',
            default=(
                'Misclassified upload: registration/insurance must be submitted under '
                'Legal documents — Vehicle, not driver license.'
            ),
        )

    def handle(self, *args, **options):
        matches = find_misclassified_driver_documents()
        if not matches:
            self.stdout.write(self.style.SUCCESS('No misclassified driver-license documents found.'))
            return

        self.stdout.write(f'Found {len(matches)} misclassified document(s):')
        for doc in matches:
            driver_name = f'{doc.driver.first_name} {doc.driver.last_name}'.strip()
            self.stdout.write(
                f'  - id={doc.id} driver={driver_name} ({doc.driver_id}) '
                f'status={doc.status} file={doc.file_name or "(no file)"}'
            )

        if not options['apply']:
            self.stdout.write(
                '\nDry run only. Re-run with --apply to reject these documents.'
            )
            return

        staff = self._resolve_staff(options['staff_username'])
        count = reject_misclassified_driver_documents(
            staff,
            reason=options['reason'],
        )
        self.stdout.write(self.style.SUCCESS(f'Rejected {count} misclassified document(s).'))

    def _resolve_staff(self, username: str) -> User:
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f'Staff user not found: {username}') from exc
            if not user.is_staff:
                raise CommandError(f'User is not staff: {username}')
            return user

        user = User.objects.filter(is_staff=True).order_by('id').first()
        if not user:
            raise CommandError('No staff user found. Create one or pass --staff-username.')
        return user
