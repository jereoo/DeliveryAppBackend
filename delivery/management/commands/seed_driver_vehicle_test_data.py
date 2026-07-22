"""Replace driver/vehicle/legal-document rows with catalog-compliant test profiles."""
import os

from django.core.management.base import BaseCommand, CommandError

from delivery.seed_driver_vehicle_test_data import seed_driver_vehicle_test_data


class Command(BaseCommand):
    help = (
        'Clear all drivers, vehicles, driver assignments, and legal documents, then seed '
        'catalog-compliant test.driver.* accounts with legal document scenarios. '
        'Does not modify customers or deliveries.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing driver/vehicle/legal-document rows and recreate test profiles',
        )

    def handle(self, *args, **options):
        self._guard_production()

        result = seed_driver_vehicle_test_data(force=options['force'])

        if result.get('skipped'):
            self.stdout.write(self.style.WARNING(f"Skipped: {result.get('reason')}"))
            return

        cleared = result['cleared']
        self.stdout.write(self.style.SUCCESS('Driver/vehicle test seed complete.'))
        self.stdout.write(
            f"  Cleared: {cleared['drivers']} drivers, {cleared['vehicles']} vehicles, "
            f"{cleared['legal_documents']} legal documents"
        )
        self.stdout.write(f"  Password (all test drivers): {result['password']}")
        self.stdout.write(f"  Staff user for doc verification: {result['staff_username']}")
        self.stdout.write('')
        for profile in result['profiles']:
            self.stdout.write(
                f"  {profile['username']:24} driver={profile['driver_id']} "
                f"vehicle={profile['vehicle_plate']} "
                f"approval={profile['approval_status']} "
                f"docs={profile['legal_documents']} ({profile['doc_scenario']})"
            )

    def _guard_production(self):
        on_heroku = bool(os.environ.get('DYNO'))
        allow = os.environ.get('ALLOW_DEMO_SEED', '').strip() == '1'
        if on_heroku and not allow:
            raise CommandError(
                'Refusing to seed on Heroku without ALLOW_DEMO_SEED=1. '
                'Use only on staging/local, never production truck-buddy.'
            )
