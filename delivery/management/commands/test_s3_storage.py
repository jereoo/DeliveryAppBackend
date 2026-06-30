"""Run live S3 smoke tests against AWS credentials in the environment."""
from django.core.management.base import BaseCommand, CommandError

from delivery.s3_smoke import all_passed, format_smoke_report, run_s3_smoke_tests


class Command(BaseCommand):
    help = (
        'Verify compliance S3 bucket access (head, put, get, presigned URLs). '
        'Uses AWS_* env vars. On Heroku: heroku run python manage.py test_s3_storage -a truck-buddy'
    )

    def handle(self, *args, **options):
        results = run_s3_smoke_tests()
        report = format_smoke_report(results)
        self.stdout.write(report)
        if not all_passed(results):
            raise CommandError('S3 smoke test failed — see steps above.')
