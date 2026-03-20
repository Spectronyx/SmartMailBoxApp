"""
Task models for the Smart Mailbox Summarizer system.

This module defines the Task model which represents actionable items
extracted from emails.
"""

from django.db import models
from emails.models import Email


class Task(models.Model):
    """
    Represents an actionable task extracted from an email.
    
    Design Decision: Tasks are tightly coupled to emails via FK.
    The reminder_sent flag will be used by a future background job
    (e.g., Celery) to send deadline reminders.
    """
    
    # Core task fields
    action_text = models.TextField(
        help_text="Description of the action to be taken"
    )
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this task needs to be completed"
    )
    reminder_sent = models.BooleanField(
        default=False,
        help_text="Whether a reminder has been sent for this task"
    )
    
    # Relationships
    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="The email this task was extracted from"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['deadline']
        indexes = [
            models.Index(fields=['deadline']),
            models.Index(fields=['reminder_sent', 'deadline']),
        ]
    
    def __str__(self):
        return f"Task: {self.action_text[:50]} (Due: {self.deadline.date() if self.deadline else 'No deadline'})"
        
    def save(self, *args, **kwargs):
        """
        Always ensure action_text is plain text without HTML tags before saving.
        """
        from emails.utils.text_processing import preprocess_for_ai
        if self.action_text:
            self.action_text = preprocess_for_ai(self.action_text)
        super().save(*args, **kwargs)
