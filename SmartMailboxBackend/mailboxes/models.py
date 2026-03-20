"""
Mailbox models for the Smart Mailbox Summarizer system.

This module defines the Mailbox model which represents email accounts
that the system monitors and processes.
"""

from django.db import models
from django.contrib.auth.models import User


class Mailbox(models.Model):
    """
    Represents an email mailbox/account to be monitored.
    
    Design Decision: We store provider info separately to allow for
    provider-specific integration logic in the future (e.g., Gmail API,
    Outlook API, IMAP, etc.)
    """
    
    PROVIDER_CHOICES = [
        ('GMAIL', 'Gmail'),
        ('OUTLOOK', 'Outlook'),
        ('YAHOO', 'Yahoo'),
        ('IMAP', 'Generic IMAP'),
        ('OTHER', 'Other'),
    ]
    
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        help_text="Email service provider"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mailboxes',
        null=True,
        blank=True,
        help_text="User who owns this mailbox"
    )
    email_address = models.EmailField(
        unique=True,
        help_text="Email address of the mailbox"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this mailbox is actively being monitored"
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this mailbox was last synced"
    )
    
    # Connection Settings
    imap_server = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="IMAP server address (e.g., imap.gmail.com)"
    )
    imap_port = models.IntegerField(
        default=993,
        help_text="IMAP server port (usually 993 for SSL)"
    )
    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Username for IMAP login (defaults to email_address if empty)"
    )
    password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="App Password or account password"
    )
    use_ssl = models.BooleanField(
        default=True,
        help_text="Whether to use SSL for the connection"
    )
    
    # Metadata fields for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mailbox"
        verbose_name_plural = "Mailboxes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email_address} ({self.get_provider_display()})"
