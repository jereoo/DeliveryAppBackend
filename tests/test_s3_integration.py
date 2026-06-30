"""Optional live S3 integration tests — skipped in CI unless RUN_S3_INTEGRATION=1."""

import os
import unittest

from django.test import SimpleTestCase

from delivery.s3_smoke import all_passed, format_smoke_report, run_s3_smoke_tests


@unittest.skipUnless(
    os.environ.get('RUN_S3_INTEGRATION') == '1',
    'Set RUN_S3_INTEGRATION=1 to run live S3 tests against AWS_* env vars.',
)
class S3IntegrationSmokeTests(SimpleTestCase):
    def test_s3_compliance_bucket_smoke(self):
        results = run_s3_smoke_tests()
        if not all_passed(results):
            self.fail(format_smoke_report(results))
