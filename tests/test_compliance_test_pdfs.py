# Compliance test PDF generator

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from delivery.compliance_test_pdfs import (
    SAMPLE_DOCUMENTS,
    build_sample_pdf,
    write_sample_documents,
)


class ComplianceTestPdfGeneratorTests(SimpleTestCase):
    def test_build_sample_pdf_starts_with_pdf_header(self):
        sample = SAMPLE_DOCUMENTS[0]
        data = build_sample_pdf(sample.title, sample.lines)
        self.assertTrue(data.startswith(b'%PDF-1.4'))
        self.assertIn(b'%%EOF', data)
        self.assertIn(b'TEST ONLY', data)

    def test_write_sample_documents_creates_all_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_sample_documents(Path(tmp))
            self.assertEqual(len(paths), len(SAMPLE_DOCUMENTS))
            for sample in SAMPLE_DOCUMENTS:
                path = Path(tmp) / sample.filename
                self.assertTrue(path.exists())
                self.assertGreater(path.stat().st_size, 200)
