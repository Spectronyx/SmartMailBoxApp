"""
Serializers for the Mailbox app.

This module provides DRF serializers for converting Mailbox model
instances to/from JSON representations.
"""

from rest_framework import serializers
from .models import Mailbox


class MailboxSerializer(serializers.ModelSerializer):
    """
    Serializer for the Mailbox model.
    
    Provides full CRUD serialization with validation for email addresses
    and provider choices.
    """
    
    # Read-only fields for metadata
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Mailbox
        fields = [
            'id',
            'user',
            'provider',
            'email_address',
            'is_active',
            'last_synced_at',
            'imap_server',
            'imap_port',
            'username',
            'password',
            'use_ssl',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'last_synced_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_email_address(self, value):
        """
        Ensure email addresses are lowercase for consistency.
        """
        return value.lower()
