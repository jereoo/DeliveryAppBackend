"""Serializers for staff user admin API (Phase 4G)."""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import StaffProfile
from .registration_messages import EMAIL_TAKEN, USERNAME_TAKEN
from .staff_constants import StaffRole
from .staff_service import create_staff_user, update_staff_profile


class StaffUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'staff_role',
            'job_title',
            'phone_number',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'created_at',
            'updated_at',
        ]


class StaffUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    staff_role = serializers.ChoiceField(choices=StaffRole.choices)
    job_title = serializers.CharField(required=False, allow_blank=True, default='')
    phone_number = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(USERNAME_TAKEN)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(EMAIL_TAKEN)
        return value

    def create(self, validated_data):
        actor = self.context['request'].user
        return create_staff_user(actor, **validated_data)


class StaffUserUpdateSerializer(serializers.Serializer):
    staff_role = serializers.ChoiceField(choices=StaffRole.choices, required=False)
    job_title = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def update(self, instance: StaffProfile, validated_data):
        actor = self.context['request'].user
        return update_staff_profile(actor, instance, **validated_data)
