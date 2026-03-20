"""
Views for the Task app.

This module provides REST API endpoints for managing tasks.
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations.
    
    Provides:
    - list: GET /api/tasks/
    - create: POST /api/tasks/
    - retrieve: GET /api/tasks/{id}/
    - update: PUT/PATCH /api/tasks/{id}/
    - destroy: DELETE /api/tasks/{id}/
    
    Design Decision: Tasks can be filtered by deadline and reminder status
    to support features like "upcoming tasks" and "tasks needing reminders".
    """
    
    queryset = Task.objects.select_related('email', 'email__mailbox').all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['email', 'reminder_sent']
    search_fields = ['action_text']
    ordering_fields = ['deadline', 'created_at']
    ordering = ['deadline']
    
    @action(detail=True, methods=['get'], url_path='export-ics')
    def export_ics(self, request, pk=None):
        """
        Export a single task as an ICS file.
        """
        from icalendar import Calendar, Event
        from django.http import HttpResponse
        from django.utils import timezone
        
        task = self.get_object()
        if not task.deadline:
            return Response({'error': 'Task has no deadline'}, status=400)
            
        cal = Calendar()
        cal.add('prodid', '-//Smart Mailbox//Task Export//EN')
        cal.add('version', '2.0')
        
        event = Event()
        event.add('summary', task.action_text)
        event.add('dtstart', task.deadline)
        event.add('dtend', task.deadline + timezone.timedelta(hours=1))
        event.add('description', f"Extracted from email: {task.email.subject}\nSender: {task.email.sender}")
        event.add('uid', f"task-{task.id}@smartmailbox")
        
        cal.add_component(event)
        
        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="task-{task.id}.ics"'
        return response

    @action(detail=False, methods=['get'], url_path='export-calendar')
    def export_calendar(self, request):
        """
        Export all tasks with deadlines as a full ICS calendar.
        """
        from icalendar import Calendar, Event
        from django.http import HttpResponse
        from django.utils import timezone
        
        tasks = Task.objects.filter(deadline__isnull=False)
        
        cal = Calendar()
        cal.add('prodid', '-//Smart Mailbox//Full Calendar//EN')
        cal.add('version', '2.0')
        
        for task in tasks:
            event = Event()
            event.add('summary', task.action_text)
            event.add('dtstart', task.deadline)
            event.add('dtend', task.deadline + timezone.timedelta(hours=1))
            event.add('description', f"From: {task.email.sender}\nEmail: {task.email.subject}")
            event.add('uid', f"task-{task.id}@smartmailbox")
            cal.add_component(event)
            
        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="smart-mailbox-tasks.ics"'
        return response

    @action(detail=False, methods=['post'], url_path='run-reminders')
    def run_reminders(self, request):
        """
        Trigger the reminder service to check and send reminders.
        
        POST /api/tasks/run-reminders/
        
        Design Decision:
        This endpoint allows manual triggering of the reminder process.
        In production, this would be called by:
        
        1. **Scheduled Jobs**:
           - Cron job running every hour
           - Systemd timer
           - Kubernetes CronJob
        
        2. **Async Task Queue** (Preferred):
           - Celery Beat for periodic execution
           - Distributed task processing
           - Better error handling and retries
        
        Why Async?
        - Reminder processing can be time-consuming
        - Should not block HTTP requests
        - Needs to run periodically (hourly/daily)
        - Requires retry logic for failed notifications
        
        Notification Extension:
        The notification system can be extended by:
        1. Adding new notification classes (email, SMS, push)
        2. Implementing a NotificationInterface
        3. Configuring per-user notification preferences
        
        Returns:
            {
                'message': str,
                'stats': {
                    'total_checked': int,
                    'reminders_sent': int,
                    'final_reminders': int,
                    'errors': int
                }
            }
        """
        from rest_framework.decorators import action
        from rest_framework.response import Response
        import logging
        logger = logging.getLogger(__name__)
        from .services import send_reminders
        
        try:
            # Run the reminder service
            stats = send_reminders()
            
            return Response({
                'message': f'Reminder check complete. Sent {stats["reminders_sent"]} reminders.',
                'stats': stats
            })
            
        except Exception as e:
            logger.exception("Error during reminder check")
            return Response({
                'error': str(e),
                'message': 'Failed to run reminder check'
            }, status=500)
