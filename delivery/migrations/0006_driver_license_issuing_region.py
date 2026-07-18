# Driver license issuing region (province / state)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0005_driver_approval_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='license_issuing_region',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Province/state code, e.g. CA-BC or US-CA',
                max_length=8,
            ),
        ),
    ]
