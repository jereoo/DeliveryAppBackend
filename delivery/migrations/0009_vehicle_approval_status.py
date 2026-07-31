# Vehicle approval workflow (PENDING / APPROVED / RESUBMIT / REJECTED)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def approve_existing_active_vehicles(apps, schema_editor):
    Vehicle = apps.get_model('delivery', 'Vehicle')
    Vehicle.objects.filter(active=True).update(approval_status='APPROVED')


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0008_legaldocument_expiry_reminders'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='approval_status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending approval'),
                    ('APPROVED', 'Approved'),
                    ('RESUBMIT', 'Resubmit required'),
                    ('REJECTED', 'Rejected'),
                ],
                default='PENDING',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='resubmit_reason',
            field=models.TextField(
                blank=True,
                help_text='Staff message when vehicle is sent back for driver correction.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='vehicles_approved',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(approve_existing_active_vehicles, migrations.RunPython.noop),
    ]
