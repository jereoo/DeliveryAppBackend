"""Generate clearly fictional compliance PDFs for local/QA testing only."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SampleComplianceDocument:
    filename: str
    title: str
    lines: tuple[str, ...]
    document_type: str
    suggested_expiry_date: str
    suggested_effective_date: str
    issuer_or_carrier: str
    policy_or_registration_number: str


SAMPLE_DOCUMENTS: tuple[SampleComplianceDocument, ...] = (
    SampleComplianceDocument(
        filename='driver_license_sample.pdf',
        title='SAMPLE DRIVER LICENCE — TEST ONLY — NOT VALID',
        document_type='DRIVER_LICENSE',
        suggested_expiry_date='2028-12-31',
        suggested_effective_date='2024-01-01',
        issuer_or_carrier='Test Motor Registry',
        policy_or_registration_number='TEST-BC-000123',
        lines=(
            'TruckBuddy / DeliveryApp — Compliance test fixture',
            'This is fictional data for software testing only.',
            '',
            'Driver name: Alex Carter',
            'Licence number: TEST-BC-000123',
            'Licence class: 5',
            'Issuer: Test Motor Registry (fictional)',
            'Effective date: 2024-01-01',
            'Expiry date: 2028-12-31',
            'Status: PENDING admin review (test)',
        ),
    ),
    SampleComplianceDocument(
        filename='vehicle_registration_sample.pdf',
        title='SAMPLE VEHICLE REGISTRATION — TEST ONLY — NOT VALID',
        document_type='VEHICLE_REGISTRATION',
        suggested_expiry_date='2027-12-31',
        suggested_effective_date='2025-01-01',
        issuer_or_carrier='Test Motor Registry',
        policy_or_registration_number='REG-TEST-000456',
        lines=(
            'TruckBuddy / DeliveryApp — Compliance test fixture',
            'This is fictional data for software testing only.',
            '',
            'Registered owner: Alex Carter',
            'Plate: TEST123',
            'VIN: TESTVIN1234567890',
            'Make / model: Ford F-150 (2022)',
            'Colour: Blue',
            'Registration number: REG-TEST-000456',
            'Effective date: 2025-01-01',
            'Expiry date: 2027-12-31',
            'Status: PENDING admin review (test)',
        ),
    ),
    SampleComplianceDocument(
        filename='commercial_insurance_sample.pdf',
        title='SAMPLE COMMERCIAL INSURANCE — TEST ONLY — NOT VALID',
        document_type='COMMERCIAL_INSURANCE',
        suggested_expiry_date='2027-12-31',
        suggested_effective_date='2025-01-01',
        issuer_or_carrier='Test Insurance Co.',
        policy_or_registration_number='POL-TEST-78910',
        lines=(
            'TruckBuddy / DeliveryApp — Compliance test fixture',
            'This is fictional data for software testing only.',
            '',
            'Named insured: Alex Carter',
            'Carrier: Test Insurance Co. (fictional)',
            'Policy number: POL-TEST-78910',
            'Coverage type: COMMERCIAL',
            'Use: Local delivery / courier (test policy)',
            'Effective date: 2025-01-01',
            'Expiry date: 2027-12-31',
            'Status: PENDING admin review (test)',
        ),
    ),
)


def _pdf_escape(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def build_sample_pdf(title: str, lines: tuple[str, ...]) -> bytes:
    """Build a minimal valid PDF using only the standard library."""
    content_lines = [
        'BT',
        '/F1 22 Tf',
        '36 740 Td',
        f'({_pdf_escape(title)}) Tj',
        '0 -28 Td',
        '/F1 12 Tf',
    ]
    for line in lines:
        wrapped = textwrap.wrap(line, width=72) or ['']
        for part in wrapped:
            content_lines.append(f'({_pdf_escape(part)}) Tj')
            content_lines.append('0 -16 Td')
    content_lines.append('ET')
    stream = '\n'.join(content_lines).encode('latin-1', errors='replace')
    stream_header = f'<< /Length {len(stream)} >>\nstream\n'.encode('ascii')
    stream_footer = b'\nendstream'

    objects: list[bytes] = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        (
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
            b'/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>'
        ),
        stream_header + stream + stream_footer,
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    ]

    pdf = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f'{index} 0 obj\n'.encode('ascii'))
        pdf.extend(obj)
        pdf.extend(b'\nendobj\n')

    xref_start = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets[1:]:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode('ascii'))
    pdf.extend(
        f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_start}\n%%EOF\n'.encode('ascii'),
    )
    return bytes(pdf)


def write_sample_documents(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for sample in SAMPLE_DOCUMENTS:
        path = output_dir / sample.filename
        path.write_bytes(build_sample_pdf(sample.title, sample.lines))
        written.append(path)
    return written
