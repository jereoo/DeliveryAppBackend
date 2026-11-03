from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0013_password_auth'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffinvite',
            name='username',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
