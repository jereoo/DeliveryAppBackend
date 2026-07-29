# Generated manually for Phase 4D compliance expiry email reminders

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0007_vehicle_catalog'),
    ]

    operations = [
        migrations.AddField(
            model_name='legaldocument',
            name='expiry_reminder_0_sent_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the expiry-day email was sent (Phase 4D).',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='legaldocument',
            name='expiry_reminder_14_sent_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the 14-day-before-expiry email was sent (Phase 4D).',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='legaldocument',
            name='expiry_reminder_30_sent_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the 30-day-before-expiry email was sent (Phase 4D).',
                null=True,
            ),
        ),
    ]
