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
        import logging
        logger = logging.getLogger(__name__)
        mailbox = self.get_object()

        try:
            # --- Gmail API path ---
            if mailbox.provider == 'GMAIL' and hasattr(request.user, 'profile'):
                profile = request.user.profile
                if profile.google_access_token:
                    from .services import GmailService
                    
                    logger.info(f"Starting Gmail API sync for {mailbox.email_address}")
                    service = GmailService(mailbox, profile)
                    created_count = service.fetch_new_messages()
                    
                    mailbox.last_synced_at = timezone.now()
                    mailbox.save()
                    
                    return Response({
                        'message': f'Gmail API sync complete! {created_count} new emails fetched.',
                        'emails_created': created_count,
                        'mailbox': mailbox.email_address,
                        'mode': 'gmail_api'
                    })

            # --- Real IMAP path ---
            if mailbox.imap_server and mailbox.password:
                from .services import IMAPService

                logger.info(f"Starting IMAP sync for {mailbox.email_address}")
                service = IMAPService(mailbox)
                created_count = service.fetch_new_emails()

                mailbox.last_synced_at = timezone.now()
                mailbox.save()

                return Response({
                    'message': f'IMAP sync complete! {created_count} new emails fetched.',
                    'emails_created': created_count,
                    'mailbox': mailbox.email_address,
                    'mode': 'imap'
                })

            # --- Demo fallback path ---
            logger.info(f"No IMAP credentials for {mailbox.email_address}, using demo data.")
            from emails.models import Email
            from datetime import timedelta
            import random

            sample_emails = [
                {
                    'subject': 'URGENT: Project deadline moved to this Friday',
                    'sender': 'manager@company.com',
                    'body': (
                        '<p>Hi team,</p>'
                        '<p>The client has requested we move the delivery <b>deadline to this Friday</b>.</p>'
                        '<p>Please prioritize all remaining tasks and submit your work by end of day Thursday.</p>'
                        '<p>We need to review everything before the final submission. This is critical.</p>'
                    ),
                    'attachments': [
                        {'filename': 'project_brief.pdf', 'content_type': 'application/pdf', 'size': 1024500}
                    ]
                },
                {
                    'subject': 'Job Opportunity: Senior Developer at Tech Corp',
                    'sender': 'recruiter@techcorp.com',
                    'body': (
                        'We noticed your profile and think you would be a <i>great fit</i> for our <b>Senior Developer</b> role.'
                        '<br><br>The position offers competitive salary, remote work, and stock options.'
                        '<br>Would you be interested in scheduling a call this week?'
                    ),
                },
                {
                    'subject': 'Weekly Newsletter: Tech Giants 2026',
                    'sender': 'news@techdigest.io',
                    'body': (
                        '<div style="color: #333; font-family: sans-serif;">'
                        '<h1>Tech Weekly</h1>'
                        '<p>This week we explore the rise of <b>Gemini 3</b> and its impact on the developer ecosystem.</p>'
                        '<ul><li>LLMs in the browser</li><li>The end of manual inbox management?</li></ul>'
                        '</div>'
                    ),
                    'attachments': [
                        {'filename': 'weekly_stats.xlsx', 'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'size': 45000}
                    ]
                },
                {
                    'subject': 'Invoice #4521 - CloudHost IO',
                    'sender': 'billing@cloudhost.io',
                    'body': (
                        'Your monthly hosting invoice is ready. <b>Amount due: $49.99</b>.<br>'
                        'Payment deadline: February 20, 2026.<br>'
                        'Please see the attached PDF for details.'
                    ),
                    'attachments': [
                        {'filename': 'invoice_4521.pdf', 'content_type': 'application/pdf', 'size': 85000}
                    ]
                }
            ]

            now = timezone.now()
            created_count = 0

            for email_data in sample_emails:
                exists = Email.objects.filter(
                    mailbox=mailbox,
                    subject=email_data['subject'],
                    sender=email_data['sender']
                ).exists()

                if not exists:
                    email_obj = Email.objects.create(
                        mailbox=mailbox,
                        subject=email_data['subject'],
                        sender=email_data['sender'],
                        body=email_data['body'],
                        received_at=now - timedelta(hours=random.randint(1, 72)),
                    )
                    
                    # Create demo attachments
                    if 'attachments' in email_data:
                        from emails.models import Attachment
                        for att_data in email_data['attachments']:
                            Attachment.objects.create(
                                email=email_obj,
                                filename=att_data['filename'],
                                content_type=att_data['content_type'],
                                size=att_data['size']
                            )

                    # Run auto-pipeline asynchronously for demo visibility
                    from emails.tasks import process_email_pipeline
                    process_email_pipeline.delay(email_obj.id)
                    
                    created_count += 1

            mailbox.last_synced_at = now
            mailbox.save()

            return Response({
                'message': (
                    f'Demo sync complete! {created_count} sample emails loaded. '
                    'Configure IMAP credentials for real email sync.'
                ),
                'emails_created': created_count,
                'mailbox': mailbox.email_address,
                'mode': 'demo'
            })

        except Exception as e:
            logger.exception(f"Error syncing mailbox {mailbox.id}")
            return Response({
                'error': 'Sync failed',
                'details': str(e)
            }, status=500)
