"""
Serializers for the Email app.

This module provides DRF serializers for Email model instances,
including nested representations for related data.
"""

from rest_framework import serializers
from .models import Email, Attachment
from mailboxes.serializers import MailboxSerializer


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attachment model.
    """
    class Meta:
        model = Attachment
        fields = ['id', 'filename', 'content_type', 'size', 'file', 'created_at']


class TaskMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal representation of a Task for nested fields.
    """
    class Meta:
        from tasks.models import Task
        model = Task
        fields = ['id', 'action_text', 'deadline', 'reminder_sent']


class EmailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Email model.
    
    Design Decision: We include a nested mailbox representation for
    read operations to provide context, but accept mailbox ID for writes
    to keep the API simple.
    """
    
    # Nested serializers for read operations
    mailbox_detail = MailboxSerializer(source='mailbox', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    tasks = TaskMinimalSerializer(many=True, read_only=True)
    
    # Read-only fields
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Email
        fields = [
            'id',
            'subject',
            'sender',
            'body',
            'received_at',
            'category',
            'summary',
            'extracted_deadline',
            'mailbox',
            'mailbox_detail',
            'attachments',
            'tasks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_sender(self, value):
        """
        Ensure sender email addresses are lowercase for consistency.
        """
        return value.lower()


class EmailListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for email lists (unified inbox).
    
    Design Decision: Excludes the full body to improve performance
    when listing many emails. Use the detail endpoint to get full content.
    """
    
    mailbox_email = serializers.EmailField(source='mailbox.email_address', read_only=True)
    snippet = serializers.SerializerMethodField()
    has_attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = Email
        fields = [
            'id',
            'subject',
            'sender',
            'received_at',
            'category',
            'summary',
            'snippet',
            'mailbox',
            'mailbox_email',
            'has_attachments',
        ]

    def get_has_attachments(self, obj):
        return obj.attachments.exists()

    def get_snippet(self, obj):
        if not obj.body:
            return ""
        from emails.utils.text_processing import preprocess_for_ai
        return preprocess_for_ai(obj.body)[:200]
