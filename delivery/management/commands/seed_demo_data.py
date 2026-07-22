"""Load idempotent demo seed data for dev/staging QA."""
import os

from django.core.management.base import BaseCommand, CommandError

from delivery.seed_demo import any_fleet_data_exists, seed_demo_data


class Command(BaseCommand):
    help = (
        'Seed a small demo dataset (demo.driver, demo.customer, one vehicle, one delivery). '
        'Safe for staging; blocked on production unless ALLOW_DEMO_SEED=1.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Replace existing demo.* users and demo vehicle/delivery',
        )
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Skip if any drivers already exist (fresh DB only)',
        )

    def handle(self, *args, **options):
        self._guard_production()

        if options['if_empty'] and any_fleet_data_exists():
            self.stdout.write(self.style.WARNING(
                'Skipped: fleet data already exists. Use --force to replace demo rows only.'
            ))
            return

        result = seed_demo_data(force=options['force'])

        if result.get('skipped'):
            self.stdout.write(self.style.WARNING(f"Skipped: {result.get('reason')}"))
            return

        self.stdout.write(self.style.SUCCESS('Demo seed complete.'))
        self.stdout.write(f"  Driver:   {result['driver_username']} / see docs/SEED_DATA.md")
        self.stdout.write(f"  Customer: {result['customer_username']} / see docs/SEED_DATA.md")
        self.stdout.write(f"  Vehicle:  {result['vehicle_plate']} (catalog spec id={result['vehicle_model_spec_id']})")
        self.stdout.write(f"  Legal docs: {result['legal_documents']} verified")
        self.stdout.write(f"  Delivery: id={result['delivery_id']}")

    def _guard_production(self):
        on_heroku = bool(os.environ.get('DYNO'))
        allow = os.environ.get('ALLOW_DEMO_SEED', '').strip() == '1'
        if on_heroku and not allow:
            raise CommandError(
                'Refusing to seed on Heroku without ALLOW_DEMO_SEED=1. '
                'Use only on staging, never production truck-buddy.'
            )
