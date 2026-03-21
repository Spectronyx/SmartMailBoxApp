"""
Views for the Mailbox app.

This module provides REST API endpoints for managing mailboxes,
including a sync endpoint to fetch/generate emails.
"""

from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Mailbox
from .serializers import MailboxSerializer


class MailboxViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Mailbox CRUD operations.
    
    Provides:
    - list: GET /api/mailboxes/
    - create: POST /api/mailboxes/
    - retrieve: GET /api/mailboxes/{id}/
    - update: PUT /api/mailboxes/{id}/
    - partial_update: PATCH /api/mailboxes/{id}/
    - destroy: DELETE /api/mailboxes/{id}/
    - sync_emails: POST /api/mailboxes/{id}/sync_emails/
    
    Design Decision: Using ModelViewSet for full CRUD as mailboxes
    need to be manageable by users (add/remove email accounts).
    """
    
    queryset = Mailbox.objects.all()
    serializer_class = MailboxSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider', 'is_active']
    search_fields = ['email_address']
    ordering_fields = ['created_at', 'email_address']
    ordering = ['-created_at']

    def get_queryset(self):
        """Users only see their own mailboxes."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assign the mailbox to the current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post'], url_path='sync_settings')
    def sync_settings(self, request):
        """
        Get or update the global sync interval for all mailboxes.
        
        GET /api/mailboxes/sync_settings/
        POST /api/mailboxes/sync_settings/ {'interval_minutes': int}
        """
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        import logging
        logger = logging.getLogger(__name__)
        
        task_name = 'sync-all-mailboxes-every-5-minutes' # Default name from celery.py
        
        if request.method == 'GET':
            try:
                task = PeriodicTask.objects.get(name=task_name)
                return Response({
                    'interval_minutes': task.interval.every,
                    'period': task.interval.period,
                    'is_active': task.enabled
                })
            except PeriodicTask.DoesNotExist:
                # If not in DB, it might be in celery.py defaults
                return Response({
                    'interval_minutes': 5,
                    'period': 'minutes',
                    'is_active': True,
                    'note': 'Using system defaults'
                })

        # POST: Update interval
        interval_minutes = request.data.get('interval_minutes')
        if not interval_minutes or not isinstance(interval_minutes, int) or interval_minutes < 1:
            return Response({'error': 'Invalid interval_minutes. Must be at least 1.'}, status=400)

        try:
            # Get or create the interval schedule
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=interval_minutes,
                period=IntervalSchedule.MINUTES,
            )
            
            # Get or create the periodic task
            task, created = PeriodicTask.objects.get_or_create(
                name=task_name,
                defaults={
                    'task': 'mailboxes.sync_all_mailboxes',
                    'interval': schedule,
                    'enabled': True,
                }
            )
            
            if not created:
                task.interval = schedule
                task.save()
                
            return Response({
                'message': f'Sync interval updated to {interval_minutes} minutes.',
                'interval_minutes': interval_minutes
            })
        except Exception as e:
            logger.exception("Failed to update sync settings")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='trigger_sync')
    def trigger_sync(self, request):
        """
        Manually trigger a sync for all active mailboxes.
        
        POST /api/mailboxes/trigger_sync/
        Useful for external cron jobs (e.g. cron-job.org) when Celery Beat is unavailable.
        """
        from .tasks import sync_all_mailboxes
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Manual trigger_sync called")
            result = sync_all_mailboxes()
            return Response({'message': 'Sync triggered successfully', 'result': result})
        except Exception as e:
            logger.exception("Manual trigger_sync failed")
            return Response({'error': str(e)}, status=500)


    @action(detail=True, methods=['post'], url_path='sync_emails')
    def sync_emails(self, request, pk=None):
        """
        Sync (fetch) emails for this mailbox.

        POST /api/mailboxes/{id}/sync_emails/

        If the mailbox has IMAP credentials configured (imap_server + password),
        it connects to the real server and fetches UNSEEN emails.

        If no credentials are set, it falls back to generating sample demo emails
        so the AI classification pipeline can still be demonstrated.

        Returns:
            {
                'message': str,
                'emails_created': int,
                'mailbox': str,
                'mode': 'imap' | 'demo'
            }
        """
        import threading
        import logging
        from django.db import connection
        from .tasks import sync_mailbox_task

        logger = logging.getLogger(__name__)
        mailbox = self.get_object()

        def _background_sync():
            """Run sync in a background thread to avoid Render's 30s timeout."""
            try:
                sync_mailbox_task(mailbox.id)
            except Exception as e:
                logger.exception(f"Background sync failed for mailbox {mailbox.id}: {e}")
            finally:
                connection.close()

        thread = threading.Thread(target=_background_sync, daemon=True)
        thread.start()

        return Response({
            'message': f'Sync started for {mailbox.email_address}. Refresh in a few seconds.',
            'mailbox': mailbox.email_address,
            'status': 'syncing'
        })
