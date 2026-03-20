"""
Admin configuration for the Email app.
"""

from django.contrib import admin
from .models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    """
    Admin interface for Email model.
    """
    list_display = ['subject', 'sender', 'mailbox', 'category', 'received_at']
    list_filter = ['category', 'mailbox', 'received_at']
    search_fields = ['subject', 'sender', 'body']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'received_at'
