"""
Serializers for the Task app.

This module provides DRF serializers for Task model instances.
"""

from rest_framework import serializers
from .models import Task
from emails.serializers import EmailListSerializer


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    
    Design Decision: Include a nested email summary to provide context
    about which email the task originated from.
    """
    
    # Nested email info for context
    email_detail = EmailListSerializer(source='email', read_only=True)
    
    # Read-only fields
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id',
            'action_text',
            'deadline',
            'reminder_sent',
            'email',
            'email_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
