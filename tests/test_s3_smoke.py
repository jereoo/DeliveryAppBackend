"""Unit tests for S3 smoke harness (no live AWS required)."""

import os
from unittest.mock import patch

from django.test import SimpleTestCase

from delivery import compliance_storage
from delivery.s3_smoke import all_passed, format_smoke_report, run_s3_smoke_tests


class S3SmokeHarnessTests(SimpleTestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_env_stops_at_first_step(self):
        results = run_s3_smoke_tests()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'env_configured')
        self.assertFalse(results[0].ok)
        self.assertIn('AWS', results[0].detail)
        self.assertFalse(all_passed(results))

    def test_format_smoke_report_includes_pass_fail(self):
        from delivery.s3_smoke import SmokeStepResult

        report = format_smoke_report([
            SmokeStepResult('env_configured', True, 'bucket=b region=r'),
            SmokeStepResult('head_bucket', False, 'AccessDenied'),
        ])
        self.assertIn('[PASS] env_configured', report)
        self.assertIn('[FAIL] head_bucket', report)
        self.assertIn('1/2 passed', report)

    def test_normalize_aws_region_from_console_label(self):
        self.assertEqual(
            compliance_storage.normalize_aws_region('Canada (Central) ca-central-1'),
            'ca-central-1',
        )
        self.assertEqual(compliance_storage.normalize_aws_region('us-east-1'), 'us-east-1')
        self.assertEqual(compliance_storage.normalize_aws_region(''), 'us-east-1')
