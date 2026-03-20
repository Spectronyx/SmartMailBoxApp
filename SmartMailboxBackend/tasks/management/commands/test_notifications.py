from django.core.management.base import BaseCommand
from tasks.services.reminder_service import ReminderService
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Test the multi-channel notification system.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking for existing tasks to run a test sweep...")
        
        # Ensure we have at least one task for testing
        task = Task.objects.first()
        if not task:
            self.stdout.write(self.style.WARNING("No tasks found in DB. Please sync emails first."))
            return

        self.stdout.write(f"Testing notifications with Task ID: {task.id}")
        
        service = ReminderService()
        
        # Force a reminder regardless of deadline checking
        urgency = "🟡 TEST"
        window = "test_window"
        
        sent_count = 0
        for channel in service.channels:
            name = channel.__class__.__name__
            self.stdout.write(f"  Sending test to {name}...")
            if channel.send(task, window, urgency, ""):
                self.stdout.write(self.style.SUCCESS(f"  Successfully sent via {name}"))
                sent_count += 1
            else:
                self.stdout.write(self.style.ERROR(f"  Failed via {name}"))
        
        self.stdout.write(f"Test complete. Total successful channels: {sent_count}")
