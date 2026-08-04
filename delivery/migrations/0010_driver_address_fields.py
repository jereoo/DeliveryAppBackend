# Driver home address fields (mirror Customer address structure)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0009_vehicle_approval_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='address_unit',
            field=models.CharField(blank=True, help_text='Unit/Apartment number', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='address_street',
            field=models.CharField(blank=True, help_text='Street address', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='address_city',
            field=models.CharField(blank=True, help_text='City', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='address_state',
            field=models.CharField(blank=True, help_text='State/Province', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='address_postal_code',
            field=models.CharField(blank=True, help_text='Postal/ZIP code', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='address_country',
            field=models.CharField(
                choices=[('CA', 'Canada'), ('US', 'United States')],
                default='US',
                help_text='Country',
                max_length=2,
            ),
        ),
    ]
