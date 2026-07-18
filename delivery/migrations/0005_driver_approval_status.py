# Generated manually for driver registration approval workflow

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0004_legal_document_phase_4a'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='approval_status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending approval'),
                    ('APPROVED', 'Approved'),
                    ('REJECTED', 'Rejected'),
                ],
                default='APPROVED',
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name='driver',
            name='approval_rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_drivers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
