# Generated migration to make vehicle fields non-nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0013_populate_vehicle_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='make',
            field=models.CharField(help_text='Vehicle manufacturer (e.g., Ford, Toyota)', max_length=50),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='model',
            field=models.CharField(help_text='Vehicle model (e.g., Transit, Hiace)', max_length=50),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='year',
            field=models.PositiveIntegerField(help_text='Manufacturing year'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vin',
            field=models.CharField(help_text='Vehicle Identification Number', max_length=17, unique=True),
        ),
    ]