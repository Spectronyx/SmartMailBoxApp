"""
Auto-Pipeline Runner.

Orchestrates the classification, summarization, and task extraction
for newly fetched emails.
"""

import logging
from emails.services import get_classifier
from emails.services.summarizer.pipeline import get_summarizer_pipeline
from emails.services.extractor.pipeline import get_extraction_pipeline
from tasks.models import Task

logger = logging.getLogger(__name__)

def run_full_pipeline(email):
    """
    Runs the complete processing pipeline for an email.
    
    1. Classification (Gemini/ML)
    2. Summarization (Gemini/Frequency)
    3. Task Extraction (Gemini/Rules)
    """
    logger.info(f"Running auto-pipeline for email: {email.id} - {email.subject[:50]}")
    
    # 1. Classification
    try:
        classifier = get_classifier()
        classification = classifier.classify(
            sender=email.sender,
            subject=email.subject,
            body=email.body
        )
        email.category = classification['category']
        email.save()
        logger.debug(f"Classification: {email.category}")
    except Exception as e:
        logger.error(f"Auto-pipeline classification failed: {e}")

    # 2. Summarization
    try:
        summarizer = get_summarizer_pipeline()
        summary = summarizer.process(email.body, email.subject)
        if summary:
            email.summary = summary
            email.save()
            logger.debug("Summary generated")
    except Exception as e:
        logger.error(f"Auto-pipeline summarization failed: {e}")

    # 3. Task Extraction
    # Only run for non-JUNK emails as per user request
    if email.category == 'JUNK':
        logger.info(f"Skipping task extraction for JUNK email {email.id}")
        return

    try:
        extractor = get_extraction_pipeline()
        extraction_result = extractor.process(
            email_body=email.body,
            email_subject=email.subject,
            email_summary=email.summary
        )
        
        if extraction_result and extraction_result.get('should_create_task'):
            Task.objects.create(
                email=email,
                action_text=extraction_result['action_text'],
                deadline=extraction_result['deadline']
            )
            logger.debug("Task extracted")
    except Exception as e:
        logger.error(f"Auto-pipeline task extraction failed: {e}")

    logger.info(f"Auto-pipeline complete for email: {email.id}")
