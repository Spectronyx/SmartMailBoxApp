"""
Django Management Command: Send Task Reminders

This command checks for tasks with upcoming deadlines and sends reminders.

Usage:
    python manage.py send_reminders

Scheduling Options:
    
    1. Manual execution (demo purposes):
       python manage.py send_reminders
    
    2. Cron job (Unix/Linux):
       # Run every hour
       0 * * * * cd /path/to/project && python manage.py send_reminders
    
    3. Systemd timer (Linux):
       Create a systemd service + timer to run periodically
    
    4. Celery Beat (production):
       Replace with Celery periodic task for better reliability

Design Decision:
    Django management commands are synchronous and simple.
    For production, consider Celery for:
    - Asynchronous execution
    - Better error handling and retries
    - Monitoring and logging
    - Distributed task processing
"""

from django.core.management.base import BaseCommand
from tasks.services import send_reminders


class Command(BaseCommand):
    help = 'Send reminders for tasks with upcoming deadlines'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No reminders will be sent'))
            # In dry run, we would just show tasks without sending
            # For now, we'll skip implementation as it's similar
            self.stdout.write('Dry run not fully implemented')
            return
        
        self.stdout.write('Starting reminder check...\n')
        
        try:
            # Run the reminder service
            stats = send_reminders()
            
            # Display results
            self.stdout.write(self.style.SUCCESS('\n' + '='*70))
            self.stdout.write(self.style.SUCCESS('REMINDER CHECK COMPLETE'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(f"Tasks checked: {stats['total_checked']}")
            self.stdout.write(f"Reminders sent: {stats['reminders_sent']}")
            self.stdout.write(f"Final reminders: {stats['final_reminders']}")
            
            if stats['errors'] > 0:
                self.stdout.write(self.style.ERROR(f"Errors: {stats['errors']}"))
            
            self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running reminder check: {e}'))
            raise
