"""
Admin configuration for the Task app.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Task model.
    """
    list_display = ['action_text', 'deadline', 'reminder_sent', 'email', 'created_at']
    list_filter = ['reminder_sent', 'deadline']
    search_fields = ['action_text', 'email__subject']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'deadline'
