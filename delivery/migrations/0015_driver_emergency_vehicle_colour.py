from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0014_staff_invite_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='emergency_contact_name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='driver',
            name='emergency_contact_phone',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='colour',
            field=models.CharField(blank=True, default='', help_text='Exterior colour for identification', max_length=40),
        ),
    ]
