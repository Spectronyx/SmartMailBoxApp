"""
Email models for the Smart Mailbox Summarizer system.

This module defines the Email model which stores email messages
and their ML-generated metadata (category, summary, deadlines).
"""

from django.db import models
from mailboxes.models import Mailbox


class Email(models.Model):
    """
    Represents an email message with ML-enhanced metadata.
    
    Design Decision: Category and summary fields are prepared for future
    ML/NLP integration. The extracted_deadline field will be populated
    by an NLP pipeline that identifies time-sensitive information.
    """
    
    CATEGORY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('OPPORTUNITY', 'Opportunity'),
        ('INFO', 'Information'),
        ('JUNK', 'Junk'),
    ]
    
    # Core email fields
    subject = models.CharField(
        max_length=500,
        help_text="Email subject line"
    )
    sender = models.EmailField(
        help_text="Email address of the sender"
    )
    body = models.TextField(
        help_text="Full email body content"
    )
    received_at = models.DateTimeField(
        help_text="When the email was received"
    )
    
    # ML-enhanced fields (to be populated by future ML modules)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        help_text="ML-classified category of the email"
    )
    summary = models.TextField(
        null=True,
        blank=True,
        help_text="AI-generated summary of the email content"
    )
    snippet = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Plain text snippet for list views"
    )
    extracted_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="NLP-extracted deadline from email content"
    )
    
    # Relationships
    mailbox = models.ForeignKey(
        Mailbox,
        on_delete=models.CASCADE,
        related_name='emails',
        help_text="The mailbox this email belongs to"
    )
    message_id = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="RFC 2822 Message-ID header for deduplication"
    )
    
    # AI processing status
    ai_processed = models.BooleanField(
        default=False,
        help_text="Whether this email has been processed by the AI pipeline"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['-received_at']),
            models.Index(fields=['mailbox', '-received_at']),
            models.Index(fields=['category']),
            models.Index(fields=['mailbox', 'ai_processed', '-received_at']),
            models.Index(fields=['mailbox', 'message_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['mailbox', 'message_id'],
                name='unique_message_per_mailbox',
                condition=models.Q(message_id__isnull=False),
            ),
        ]
    
    def __str__(self):
        return f"{self.subject[:50]} - {self.sender}"

    def save(self, *args, **kwargs):
        """
        Always ensure summary is plain text without HTML tags and populate snippet.
        """
        from emails.utils.text_processing import preprocess_for_ai
        
        # Populate snippet if missing or body changed
        if self.body and (not self.snippet or 'body' in kwargs.get('update_fields', [])):
            self.snippet = preprocess_for_ai(self.body)[:500]

        if self.summary:
            # Summary should already be fairly clean if from Gemini, 
            # but this is a safety check.
            self.summary = preprocess_for_ai(self.summary)
            
        super().save(*args, **kwargs)


class Attachment(models.Model):
    """
    Stores metadata for email attachments.
    """
    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="The email this attachment belongs to"
    )
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.IntegerField(help_text="Size in bytes")
    file = models.FileField(
        upload_to='attachments/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Actual file storage (if enabled)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
