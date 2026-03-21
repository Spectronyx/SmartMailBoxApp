"""
Admin configuration for the Email app.
"""

from django.contrib import admin
from .models import Email, Attachment


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    """
    Admin interface for Email model.
    """
    list_display = ['subject', 'sender', 'mailbox', 'category', 'ai_processed', 'received_at']
    list_filter = ['category', 'ai_processed', 'mailbox', 'received_at']
    search_fields = ['subject', 'sender', 'body', 'message_id']
    readonly_fields = ['message_id', 'created_at', 'updated_at']
    date_hierarchy = 'received_at'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Attachment model.
    """
    list_display = ['filename', 'email', 'content_type', 'size']
    list_filter = ['content_type']
    search_fields = ['filename']
