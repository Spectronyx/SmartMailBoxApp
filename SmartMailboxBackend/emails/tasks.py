from celery import shared_task
import logging
from emails.models import Email
from emails.services.pipeline_runner import run_full_pipeline

logger = logging.getLogger(__name__)

@shared_task(name="emails.process_email_pipeline")
def process_email_pipeline(email_id):
    """
    Background task to run the AI pipeline (classification, summarization, extraction)
    for a single email.
    """
    try:
        email = Email.objects.get(id=email_id)
        logger.info(f"Processing background pipeline for email {email_id}")
        run_full_pipeline(email)
        # Mark as AI-processed so it won't be reprocessed
        email.ai_processed = True
        email.save(update_fields=['ai_processed'])
        return f"Successfully processed email {email_id}"
    except Email.DoesNotExist:
        logger.error(f"Email {email_id} not found for background pipeline")
        return f"Email {email_id} not found"
    except Exception as e:
        logger.exception(f"Error in background pipeline for email {email_id}: {e}")
        return str(e)
