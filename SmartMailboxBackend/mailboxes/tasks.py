from celery import shared_task
import logging
from .models import Mailbox
from .services.imap_service import IMAPService
from .services.gmail_service import GmailService
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(name="mailboxes.sync_mailbox_task")
def sync_mailbox_task(mailbox_id):
    """
    Two-phase sync task:
      Phase 1 — Fetch ALL new emails from Gmail/IMAP/demo and save to DB.
      Phase 2 — Run AI pipeline on the latest 100 unprocessed emails only.
    """
    try:
        mailbox = Mailbox.objects.get(id=mailbox_id)
        logger.info(f"[Phase 1] Starting email fetch for mailbox {mailbox.email_address}")
        
        created_count = 0
        mode = "demo"

        # ── Phase 1: Fetch ALL emails ──────────────────────────────────
        # 1. Try Gmail API if configured
        if mailbox.provider == 'GMAIL' and mailbox.user and hasattr(mailbox.user, 'profile'):
            profile = mailbox.user.profile
            if profile.google_access_token:
                logger.debug(f"Phase 1: Gmail API for {mailbox.email_address}")
                service = GmailService(mailbox, profile)
                created_count = service.fetch_new_messages()
                mode = "gmail_api"
        
        # 2. Try IMAP if configured
        elif mailbox.imap_server and mailbox.password:
            logger.debug(f"Phase 1: IMAP for {mailbox.email_address}")
            service = IMAPService(mailbox)
            created_count = service.fetch_new_emails()
            mode = "imap"
        
        else:
            # 3. Demo fallback — no real credentials configured
            logger.info(f"No credentials for {mailbox.email_address}, loading demo data.")
            from emails.models import Email, Attachment
            from datetime import timedelta
            import random

            sample_emails = [
                {
                    'subject': 'URGENT: Project deadline moved to this Friday',
                    'sender': 'manager@company.com',
                    'body': '<p>Hi team,</p><p>The client has requested we move the delivery <b>deadline to this Friday</b>.</p><p>Please prioritize all remaining tasks.</p>',
                    'attachments': [{'filename': 'project_brief.pdf', 'content_type': 'application/pdf', 'size': 1024500}]
                },
                {
                    'subject': 'Job Opportunity: Senior Developer at Tech Corp',
                    'sender': 'recruiter@techcorp.com',
                    'body': 'We noticed your profile and think you would be a <i>great fit</i> for our <b>Senior Developer</b> role.<br><br>Would you be interested in scheduling a call?',
                },
                {
                    'subject': 'Weekly Newsletter: Tech Giants 2026',
                    'sender': 'news@techdigest.io',
                    'body': '<p>This week we explore the rise of <b>Gemini 3</b> and its impact on the developer ecosystem.</p>',
                    'attachments': [{'filename': 'weekly_stats.xlsx', 'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'size': 45000}]
                },
                {
                    'subject': 'Invoice #4521 - CloudHost IO',
                    'sender': 'billing@cloudhost.io',
                    'body': 'Your monthly hosting invoice is ready. <b>Amount due: $49.99</b>.<br>Payment deadline: February 20, 2026.',
                    'attachments': [{'filename': 'invoice_4521.pdf', 'content_type': 'application/pdf', 'size': 85000}]
                }
            ]

            now = timezone.now()
            for email_data in sample_emails:
                if not Email.objects.filter(mailbox=mailbox, subject=email_data['subject'], sender=email_data['sender']).exists():
                    email_obj = Email.objects.create(
                        mailbox=mailbox,
                        subject=email_data['subject'],
                        sender=email_data['sender'],
                        body=email_data['body'],
                        received_at=now - timedelta(hours=random.randint(1, 72)),
                    )
                    if 'attachments' in email_data:
                        for att in email_data['attachments']:
                            Attachment.objects.create(email=email_obj, filename=att['filename'], content_type=att['content_type'], size=att['size'])
                    created_count += 1
            mode = "demo"
        
        # Update last_synced_at
        mailbox.last_synced_at = timezone.now()
        mailbox.save()
        
        logger.info(f"[Phase 1] Fetch complete for {mailbox.email_address}: {created_count} new emails ({mode}).")

        # ── Phase 2: AI-process the latest 100 unprocessed emails ──────
        from emails.models import Email
        from emails.tasks import process_email_pipeline

        unprocessed = Email.objects.filter(
            mailbox=mailbox,
            ai_processed=False
        ).order_by('-received_at')[:100]

        process_count = 0
        for email_obj in unprocessed:
            try:
                process_email_pipeline(email_obj.id)
                process_count += 1
            except Exception as pipeline_err:
                logger.warning(f"Pipeline failed for email {email_obj.id}: {pipeline_err}")

        logger.info(f"[Phase 2] AI processed {process_count} emails for {mailbox.email_address}.")
        
        return {
            'status': 'success',
            'fetched': created_count,
            'ai_processed': process_count,
            'mode': mode
        }
        
    except Mailbox.DoesNotExist:
        logger.error(f"Async sync failed: Mailbox {mailbox_id} not found.")
        return {'status': 'error', 'message': 'Mailbox not found'}
    except Exception as e:
        logger.exception(f"Async sync failed for mailbox {mailbox_id}: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task(name="mailboxes.sync_all_mailboxes")
def sync_all_mailboxes():
    # ... (existing code follows)
    """
    Periodic task to sync all active mailboxes.
    Called by Celery Beat.
    """
    logger.info("Starting periodic sync for all active mailboxes")
    active_mailboxes = Mailbox.objects.filter(is_active=True)
    
    sync_results = []
    for mailbox in active_mailboxes:
        try:
            created_count = 0
            # 1. Try Gmail API if configured
            if mailbox.provider == 'GMAIL' and mailbox.user and hasattr(mailbox.user, 'profile'):
                profile = mailbox.user.profile
                if profile.google_access_token:
                    logger.debug(f"Syncing Gmail API for {mailbox.email_address}")
                    service = GmailService(mailbox, profile)
                    created_count = service.fetch_new_messages()
            
            # 2. Try IMAP if configured
            elif mailbox.imap_server and mailbox.password:
                logger.debug(f"Syncing IMAP for {mailbox.email_address}")
                service = IMAPService(mailbox)
                created_count = service.fetch_new_emails()
            
            # Update last_synced_at
            mailbox.last_synced_at = timezone.now()
            mailbox.save()
            
            sync_results.append(f"{mailbox.email_address}: {created_count} new")
            
        except Exception as e:
            logger.error(f"Failed to sync mailbox {mailbox.email_address}: {e}")
            sync_results.append(f"{mailbox.email_address}: FAILED")
            
    return f"Periodic sync complete. Results: {', '.join(sync_results)}"
