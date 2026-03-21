"""
Views for the Email app.

This module provides REST API endpoints for managing and viewing emails.
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Email
from .serializers import EmailSerializer, EmailListSerializer

from .filters import EmailFilter

class EmailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Email operations.
    """
    
    queryset = Email.objects.select_related('mailbox').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmailFilter
    search_fields = ['subject', 'sender', 'body', 'summary']
    ordering_fields = ['received_at', 'created_at']
    ordering = ['-received_at']
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list view, full serializer for detail.
        """
        if self.action == 'list':
            return EmailListSerializer
        return EmailSerializer
    
    @action(detail=False, methods=['post'], url_path='clear-data')
    def clear_data(self, request):
        """
        DANGEROUS: Clear all Emails and Tasks.
        
        POST /api/emails/clear-data/
        
        Used to reset the demo data.
        """
        from tasks.models import Task
        email_count = Email.objects.all().count()
        task_count = Task.objects.all().count()
        
        Task.objects.all().delete()
        Email.objects.all().delete()
        
        return Response({
            'message': f'Cleared {email_count} emails and {task_count} tasks.',
            'count': email_count + task_count
        })
    
    @action(detail=False, methods=['get'], url_path='unified-inbox')
    def unified_inbox(self, request):
        """
        Custom endpoint for unified inbox view across all mailboxes.
        
        GET /api/emails/unified-inbox/
        
        This is essentially the same as the list view but provides
        a semantically clear endpoint name for the frontend.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = EmailListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmailListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='mailbox/(?P<mailbox_id>[^/.]+)')
    def by_mailbox(self, request, mailbox_id=None):
        """
        Get emails for a specific mailbox.
        
        GET /api/emails/mailbox/{mailbox_id}/
        
        Design Decision: Provides a clear, RESTful way to fetch emails
        for a single mailbox without using query parameters.
        """
        queryset = self.get_queryset().filter(mailbox_id=mailbox_id)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = EmailListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmailListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='classify')
    def classify_emails(self, request):
        """
        Classify all emails with null category using hybrid classification.
        
        POST /api/emails/classify/
        
        Design Decision: This endpoint uses a hybrid approach:
        1. First applies rule-based classification (fast, deterministic)
        2. If rules return UNKNOWN, applies ML classification
        
        This provides the best of both worlds:
        - Fast classification for obvious patterns
        - ML fallback for nuanced cases
        - Explainable results (rule matches or ML confidence)
        
        Returns:
            {
                'classified_count': int,
                'results': [
                    {
                        'email_id': int,
                        'subject': str,
                        'category': str,
                        'method': 'rule' or 'ml',
                        'confidence': float or null,
                        'matched_patterns': list or null
                    }
                ]
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        from .services import get_classifier
        
        # Get all emails with null category
        emails_to_classify = Email.objects.filter(category__isnull=True)
        
        if not emails_to_classify.exists():
            return Response({
                'message': 'No emails to classify',
                'classified_count': 0,
                'results': []
            })
        
        try:
            # Get the classifier instance
            classifier = get_classifier()
            
            # Classify each email
            results = []
            for email in emails_to_classify:
                classification = classifier.classify(
                    sender=email.sender,
                    subject=email.subject,
                    body=email.body
                )
                
                # Update email category
                email.category = classification['category']
                email.save()
                
                # Prepare result
                results.append({
                    'email_id': email.id,
                    'subject': email.subject[:50],
                    'category': classification['category'],
                    'method': classification['method'],
                    'confidence': classification['confidence'],
                    'matched_patterns': classification['matched_patterns']
                })
            
            return Response({
                'message': f'Successfully classified {len(results)} emails',
                'classified_count': len(results),
                'results': results
            })
        except Exception as e:
            logger.exception("Error during email classification")
            return Response({
                'error': 'Classification failed',
                'details': str(e)
            }, status=500)

    @action(detail=False, methods=['post'], url_path='summarize')
    def summarize_emails(self, request):
        """
        Generate summaries for all emails with null summary.
        
        POST /api/emails/summarize/
        
        Design Decision:
        - Uses extractive summarization (frequency-based)
        - Skips short emails
        - Updates 'summary' field in database
        
        Returns:
            {
                'summarized_count': int,
                'results': [
                    {'email_id': int, 'subject': str, 'summary': str}
                ]
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        from .services.summarizer.pipeline import get_summarizer_pipeline
        
        # Get emails without summary
        emails_to_summarize = Email.objects.filter(summary__isnull=True)
        
        if not emails_to_summarize.exists():
            return Response({
                'message': 'No emails to summarize',
                'summarized_count': 0,
                'results': []
            })
            
        try:
            pipeline = get_summarizer_pipeline()
            results = []
            count = 0
            
            for email in emails_to_summarize:
                # Generate summary
                summary = pipeline.process(email.body, email.subject)
                
                if summary:
                    email.summary = summary
                    email.save()
                    
                    results.append({
                        'email_id': email.id,
                        'subject': email.subject[:50],
                        'summary': summary[:100] + '...' if len(summary) > 100 else summary
                    })
                    count += 1
                else:
                    # Mark as processed even if no summary generated (to avoid re-processing)
                    # For now, we leave it null or could add a flag "processed_no_summary"
                    # Design Choice: For Sprint 3, leaving null is fine as pipeline handles min-length check
                    pass
                    
            return Response({
                'message': f'Successfully summarized {count} emails',
                'summarized_count': count,
                'results': results
            })
        except Exception as e:
            logger.exception("Error during email summarization")
            return Response({
                'error': 'Summarization failed',
                'details': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'], url_path='extract-tasks')
    def extract_tasks(self, request):
        """
        Extract actionable tasks from emails.
        
        POST /api/emails/extract-tasks/
        
        Design Decision:
        - Uses dateparser for robust date extraction (handles "tomorrow", "next Friday")
        - Uses rule-based verb matching for action detection
        - Only processes emails that don't already have tasks
        - Creates Task objects linked to Email
        
        Future Improvements:
        - Use transformer models (BERT, RoBERTa) for intent classification
        - Implement dependency parsing for better subject-verb-object understanding
        - Add zero-shot classification for dynamic action detection
        
        Returns:
            {
                'tasks_created': int,
                'results': [
                    {
                        'email_id': int,
                        'subject': str,
                        'action_text': str,
                        'deadline': datetime or null
                    }
                ]
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        from .services.extractor import get_extraction_pipeline
        from tasks.models import Task
        
        # Get emails without tasks
        emails_without_tasks = Email.objects.filter(tasks__isnull=True)
        
        if not emails_without_tasks.exists():
            return Response({
                'message': 'No emails without tasks',
                'tasks_created': 0,
                'results': []
            })
        
        try:
            pipeline = get_extraction_pipeline()
            results = []
            count = 0
            
            for email in emails_without_tasks:
                # Extract task information
                extraction_result = pipeline.process(
                    email_body=email.body,
                    email_subject=email.subject,
                    email_summary=email.summary
                )
                
                if extraction_result['should_create_task']:
                    # Create Task object
                    task = Task.objects.create(
                        email=email,
                        action_text=extraction_result['action_text'],
                        deadline=extraction_result['deadline']
                    )
                    task.refresh_from_db()
                    
                    results.append({
                        'task_id': task.id,
                        'email_id': email.id,
                        'subject': email.subject[:50],
                        'action_text': task.action_text[:100] + '...' if len(task.action_text) > 100 else task.action_text,
                        'deadline': task.deadline.isoformat() if task.deadline else None
                    })
                    count += 1
            
            return Response({
                'message': f'Successfully created {count} tasks',
                'tasks_created': count,
                'results': results
            })
        except Exception as e:
            logger.exception("Error during task extraction")
            return Response({
                'error': 'Task extraction failed',
                'details': str(e)
            }, status=500)

