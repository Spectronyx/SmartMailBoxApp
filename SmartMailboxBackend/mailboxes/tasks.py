from celery import shared_task
import logging
from .models import Mailbox
from .services.imap_service import IMAPService
from .services.gmail_service import GmailService
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(name="mailboxes.sync_all_mailboxes")
def sync_all_mailboxes():
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
