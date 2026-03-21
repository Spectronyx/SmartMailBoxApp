"""
Admin configuration for the Mailbox app.
"""

from django.contrib import admin
from .models import Mailbox


@admin.register(Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    """
    Admin interface for Mailbox model.
    """
    list_display = ['email_address', 'provider', 'user', 'is_active', 'last_synced_at', 'created_at']
    list_filter = ['provider', 'is_active']
    search_fields = ['email_address']
    readonly_fields = ['last_synced_at', 'created_at', 'updated_at']
