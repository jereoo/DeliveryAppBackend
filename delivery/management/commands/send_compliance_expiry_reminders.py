"""Send compliance expiry reminder emails at 30, 14, and 0 days (Phase 4D)."""
from django.core.management.base import BaseCommand

from delivery.compliance_reminder_service import send_compliance_expiry_reminders


class Command(BaseCommand):
    help = (
        'Email drivers when verified compliance documents expire in 30, 14, or 0 days. '
        'Schedule daily on Heroku via run_compliance_daily_jobs or this command alone.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Count reminders that would send without emailing or updating rows.',
        )

    def handle(self, *args, **options):
        result = send_compliance_expiry_reminders(dry_run=options['dry_run'])
        sent = result['sent']
        prefix = 'Dry run: would send' if options['dry_run'] else 'Sent'
        self.stdout.write(
            f'{prefix} {sent[30]} (30-day), {sent[14]} (14-day), {sent[0]} (expiry-day) '
            f"reminder(s) as of {result['as_of_date']}."
        )
        if result['skipped_no_email']:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {result['skipped_no_email']} document(s) with no driver email.",
                ),
            )
