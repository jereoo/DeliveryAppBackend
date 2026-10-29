"""Serializers for staff audit + invite API (Phase 4G Slice 5)."""

from rest_framework import serializers

from .models import StaffAuditEvent, StaffInvite
from .staff_constants import StaffRole
from .staff_invite_service import create_staff_invite


class StaffAuditEventSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True, default='')
    target_username = serializers.SerializerMethodField()

    class Meta:
        model = StaffAuditEvent
        fields = [
            'id',
            'created_at',
            'event_type',
            'actor_username',
            'target_username',
            'target_email',
            'old_role',
            'new_role',
            'detail',
        ]

    def get_target_username(self, obj: StaffAuditEvent) -> str:
        if obj.target_profile_id and obj.target_profile.user_id:
            return obj.target_profile.user.username
        return ''


class StaffInviteSerializer(serializers.ModelSerializer):
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True, default='')

    class Meta:
        model = StaffInvite
        fields = [
            'id',
            'email',
            'staff_role',
            'first_name',
            'last_name',
            'invited_by_username',
            'created_at',
            'expires_at',
            'accepted_at',
        ]
        read_only_fields = fields


class StaffInviteCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    staff_role = serializers.ChoiceField(choices=StaffRole.choices)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')

    def create(self, validated_data):
        actor = self.context['request'].user
        return create_staff_invite(actor, **validated_data)


class StaffInviteValidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffInvite
        fields = ['email', 'staff_role', 'first_name', 'last_name', 'expires_at']


class StaffInviteAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
