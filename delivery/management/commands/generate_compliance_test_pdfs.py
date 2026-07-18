"""Write fictional SAMPLE compliance PDFs for upload/UI testing."""
import json

from django.core.management.base import BaseCommand

from delivery.compliance_test_pdfs import SAMPLE_DOCUMENTS, write_sample_documents


class Command(BaseCommand):
    help = (
        'Generate clearly labeled SAMPLE compliance PDFs (driver licence, registration, insurance). '
        'For local/QA only — not valid government documents.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default='tests/fixtures/compliance',
            help='Directory for generated PDFs (default: tests/fixtures/compliance)',
        )

    def handle(self, *args, **options):
        from pathlib import Path

        output_dir = Path(options['output_dir'])
        paths = write_sample_documents(output_dir)

        metadata = {
            'notice': 'Fictional test data only. Do not use in production as real compliance proof.',
            'driver_profile': {
                'name': 'Alex Carter',
                'license_number': 'TEST-BC-000123',
                'license_class': '5',
            },
            'vehicle_profile': {
                'make': 'Ford',
                'model': 'F-150',
                'year': 2022,
                'colour': 'Blue',
                'license_plate': 'TEST123',
                'vin': 'TESTVIN1234567890',
                'gvwr_kg': 3300,
            },
            'documents': [
                {
                    'file': sample.filename,
                    'document_type': sample.document_type,
                    'suggested_expiry_date': sample.suggested_expiry_date,
                    'suggested_effective_date': sample.suggested_effective_date,
                    'issuer_or_carrier': sample.issuer_or_carrier,
                    'policy_or_registration_number': sample.policy_or_registration_number,
                }
                for sample in SAMPLE_DOCUMENTS
            ],
        }
        metadata_path = output_dir / 'metadata.json'
        metadata_path.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(f'Wrote {len(paths)} sample PDFs to {output_dir}/'))
        for path in paths:
            self.stdout.write(f'  - {path.name}')
        self.stdout.write(f'  - {metadata_path.name}')
        self.stdout.write(
            '\nUpload these via the mobile web app (Admin or Driver compliance panels). '
            'Use metadata.json expiry/issuer values when filling the form.'
        )
