"""Nightly compliance maintenance: expire documents + send expiry reminders (Phase 4D)."""
from django.core.management.base import BaseCommand
from django.utils import timezone

from delivery.compliance_reminder_service import send_compliance_expiry_reminders
from delivery.compliance_service import mark_expired_documents


class Command(BaseCommand):
    help = (
        'Run nightly compliance jobs: mark expired documents, then send 30/14/0-day '
        'expiry reminder emails. Schedule on Heroku Scheduler once daily.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report actions without updating documents or sending email.',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        dry_run = options['dry_run']

        if dry_run:
            from delivery.compliance_constants import DocumentStatus
            from delivery.models import LegalDocument

            expire_count = LegalDocument.objects.filter(
                status=DocumentStatus.VERIFIED,
                expiry_date__lt=today,
            ).count()
            self.stdout.write(f'Dry run: {expire_count} document(s) would be marked EXPIRED.')
        else:
            expire_count = mark_expired_documents(as_of_date=today)
            self.stdout.write(self.style.SUCCESS(
                f'Marked {expire_count} document(s) as EXPIRED as of {today}.',
            ))

        reminder_result = send_compliance_expiry_reminders(as_of_date=today, dry_run=dry_run)
        sent = reminder_result['sent']
        prefix = 'Dry run: would send' if dry_run else 'Sent'
        self.stdout.write(
            f'{prefix} {sent[30]} (30-day), {sent[14]} (14-day), {sent[0]} (expiry-day) '
            f"reminder(s) as of {reminder_result['as_of_date']}."
        )
        if reminder_result['skipped_no_email']:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {reminder_result['skipped_no_email']} reminder(s) — no driver email.",
                ),
            )
