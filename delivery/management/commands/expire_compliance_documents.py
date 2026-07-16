"""Nightly job: mark verified compliance documents past expiry as EXPIRED (Phase 4B)."""
from django.core.management.base import BaseCommand
from django.utils import timezone

from delivery.compliance_service import mark_expired_documents


class Command(BaseCommand):
    help = (
        'Mark VERIFIED legal documents as EXPIRED when expiry_date is before today. '
        'Schedule on Heroku: heroku run python manage.py expire_compliance_documents -a truck-buddy'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print how many documents would expire without updating.',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        if options['dry_run']:
            from delivery.compliance_constants import DocumentStatus
            from delivery.models import LegalDocument

            count = LegalDocument.objects.filter(
                status=DocumentStatus.VERIFIED,
                expiry_date__lt=today,
            ).count()
            self.stdout.write(f'Dry run: {count} document(s) would be marked EXPIRED as of {today}.')
            return

        count = mark_expired_documents(as_of_date=today)
        self.stdout.write(self.style.SUCCESS(f'Marked {count} document(s) as EXPIRED as of {today}.'))
