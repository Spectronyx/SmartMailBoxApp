"""
Reminder Service for Task Management.

This module handles task deadline reminders with multi-channel support.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict
import logging
import requests
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class BaseNotificationChannel:
    """Base class for notification channels."""
    def send(self, task, window: str, urgency: str, message: str) -> bool:
        raise NotImplementedError("Subclasses must implement send()")

class EmailChannel(BaseNotificationChannel):
    """Sends notifications via email."""
    def send(self, task, window: str, urgency: str, message: str) -> bool:
        try:
            recipient = getattr(settings, 'REMINDER_RECIPIENT_EMAIL', 'user@example.com')
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Smart Mailbox <noreply@smartmailbox.local>')
            
            subject = f"{urgency} Task Reminder [{window}]: {task.action_text[:50]}"
            
            email_body = f"""Task Reminder from Smart Mailbox
{'='*50}

Action Required: {task.action_text}
Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M %Z')}
Reminder Window: {window}

Related Email:
  Subject: {task.email.subject}
  From: {task.email.sender}

This is an automated reminder from Smart Mailbox Summarizer.
"""
            send_mail(
                subject=subject,
                message=email_body,
                from_email=from_email,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"EmailChannel failed: {e}")
            return False

class WebhookChannel(BaseNotificationChannel):
    """Sends notifications via Slack/Discord webhooks."""
    def send(self, task, window: str, urgency: str, message: str) -> bool:
        webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', '')
        if not webhook_url:
            return False
            
        try:
            payload = {
                "text": f"*{urgency} Task Reminder [{window}]*\n"
                        f"> *Task:* {task.action_text}\n"
                        f"> *Deadline:* {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                        f"> *From:* {task.email.sender}"
            }
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code < 400
        except Exception as e:
            logger.error(f"WebhookChannel failed: {e}")
            return False

class ReminderService:
    """
    Manages task reminders with multi-channel support.
    """
    
    REMINDER_WINDOWS = [
        {'name': '3_days', 'hours': 72, 'is_final': False},
        {'name': '1_day', 'hours': 24, 'is_final': False},
        {'name': '3_hours', 'hours': 3, 'is_final': True},
    ]
    
    def __init__(self):
        self.channels = [EmailChannel()]
        if getattr(settings, 'SLACK_WEBHOOK_URL', ''):
            self.channels.append(WebhookChannel())
    
    def find_tasks_needing_reminders(self) -> List:
        from tasks.models import Task
        now = datetime.now(timezone.utc)
        tasks_to_remind = []
        
        tasks = Task.objects.filter(
            deadline__isnull=False,
            reminder_sent=False
        ).select_related('email')
        
        for task in tasks:
            time_until_deadline = task.deadline - now
            hours_until_deadline = time_until_deadline.total_seconds() / 3600
            
            for window in self.REMINDER_WINDOWS:
                if 0 < hours_until_deadline <= window['hours'] + 1:
                    tasks_to_remind.append({
                        'task': task,
                        'window': window['name'],
                        'is_final': window['is_final'],
                        'hours_until': hours_until_deadline
                    })
                    break
        return tasks_to_remind
    
    def run_reminder_check(self) -> Dict:
        tasks_to_remind = self.find_tasks_needing_reminders()
        stats = {'total_checked': 0, 'reminders_sent': 0, 'errors': 0}
        
        for item in tasks_to_remind:
            task = item['task']
            window = item['window']
            is_final = item['is_final']
            hours_until = item['hours_until']
            
            urgency = "🔴 URGENT" if hours_until <= 3 else "🟡 IMPORTANT" if hours_until <= 24 else "🟢 UPCOMING"
            
            sent_any = False
            for channel in self.channels:
                if channel.send(task, window, urgency, ""):
                    sent_any = True
            
            if sent_any:
                stats['reminders_sent'] += 1
                if is_final:
                    task.reminder_sent = True
                    task.save()
            else:
                stats['errors'] += 1
            
            stats['total_checked'] += 1
            
        return stats
