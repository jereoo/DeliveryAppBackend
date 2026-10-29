# Generated manually for Phase 4G Slice 5

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0011_staff_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffAuditEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('target_email', models.EmailField(blank=True, default='', max_length=254)),
                ('event_type', models.CharField(choices=[('staff_created', 'Staff created'), ('role_changed', 'Role changed'), ('deactivated', 'Deactivated'), ('reactivated', 'Reactivated'), ('invite_sent', 'Invite sent'), ('invite_accepted', 'Invite accepted')], max_length=32)),
                ('old_role', models.CharField(blank=True, default='', max_length=32)),
                ('new_role', models.CharField(blank=True, default='', max_length=32)),
                ('detail', models.TextField(blank=True, default='')),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff_audit_events_acted', to=settings.AUTH_USER_MODEL)),
                ('target_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_events', to='delivery.staffprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StaffInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=64, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('staff_role', models.CharField(choices=[('super_admin', 'Super Admin'), ('operations_admin', 'Operations Admin'), ('compliance_reviewer', 'Compliance Reviewer'), ('read_only', 'Read Only')], max_length=32)),
                ('first_name', models.CharField(blank=True, default='', max_length=150)),
                ('last_name', models.CharField(blank=True, default='', max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('accepted_profile', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accepted_invite', to='delivery.staffprofile')),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff_invites_sent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
