"""
Extraction Pipeline for creating Tasks from Emails.

This module orchestrates deadline and action extraction to create actionable tasks.
"""

from typing import Optional, Dict
from datetime import datetime
from .date_extractor import DeadlineExtractor
from .action_extractor import ActionExtractor
from .gemini_extractor import GeminiExtractor


class ExtractionPipeline:
    """
    Orchestrates extraction of deadlines and actions from emails.
    
    Flow:
    1. Extract deadline from email body/summary
    2. Extract action from email body/summary
    3. If either found (preferably both), return task data
    
    Design Decision:
    - We prioritize emails with both deadline AND action
    - If only action found, we still create a task (no deadline)
    - If only deadline found with no clear action, we use subject as action
    """
    
    def __init__(self):
        """Initialize the extraction pipeline."""
        self.deadline_extractor = DeadlineExtractor()
        self.action_extractor = ActionExtractor()
        self.gemini_extractor = GeminiExtractor()
    
    def process(self, email_body: str, email_subject: str = "", 
                email_summary: str = None) -> Dict:
        """
        Extract task information from an email.
        
        Args:
            email_body: Full email body
            email_subject: Email subject line
            email_summary: Optional pre-generated summary
            
        Returns:
            Dict with 'deadline', 'action_text', 'should_create_task'
        """
        # 0. Preprocess body to remove HTML tags and noise
        from emails.utils.text_processing import preprocess_for_ai
        cleaned_body = preprocess_for_ai(email_body or "")
        
        # Combined text sources (prioritize summary if available)
        if email_summary and len(email_summary) > 100:
            primary_text = email_summary
            fallback_text = cleaned_body
        else:
            primary_text = cleaned_body
            fallback_text = email_summary or ""
        
        # 1. Try Gemini first (Intelligent extraction)
        # Gemini does its own cleaning internally, so we can pass original body if needed,
        # but passing cleaned_body is safer to avoid context window clutter and tokens for HTML.
        gemini_result = self.gemini_extractor.extract_task(email_subject, cleaned_body)
        if gemini_result and gemini_result.get('should_create_task'):
            return gemini_result
            
        # 2. Fallback to Rule-based extraction
        deadline = self.deadline_extractor.extract_deadline(primary_text)
        if not deadline and fallback_text:
            deadline = self.deadline_extractor.extract_deadline(fallback_text)
        
        # Extract action
        action = self.action_extractor.extract_action(primary_text)
        if not action and fallback_text:
            action = self.action_extractor.extract_action(fallback_text)
        
        # Determine if we should create a task
        should_create = False
        
        if deadline and action:
            # Best case: both found
            should_create = True
        elif action:
            # Action without deadline - still create task
            should_create = True
        elif deadline:
            # Deadline without clear action - use subject as action
            should_create = True
            action = f"Action required: {email_subject}"
        
        return {
            'deadline': deadline,
            'action_text': action,
            'should_create_task': should_create
        }
    
    def process_batch(self, emails: list) -> list:
        """
        Process multiple emails.
        
        Args:
            emails: List of dicts with 'id', 'body', 'subject', 'summary'
            
        Returns:
            List of extraction results
        """
        results = []
        for email in emails:
            result = self.process(
                email_body=email.get('body', ''),
                email_subject=email.get('subject', ''),
                email_summary=email.get('summary')
            )
            
            if result['should_create_task']:
                results.append({
                    'email_id': email['id'],
                    **result
                })
        
        return results


# Singleton instance
_pipeline_instance = None


def get_extraction_pipeline() -> ExtractionPipeline:
    """Get or create singleton pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ExtractionPipeline()
    return _pipeline_instance
