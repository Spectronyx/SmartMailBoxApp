"""
Gemini-Powered Task Extractor.

Uses Gemini 2.0 Flash to identify actionable items and deadlines from emails.
"""

import logging
import json
from typing import Optional, Dict
from datetime import datetime
from ..gemini_base import GeminiService

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a highly efficient personal assistant. Your goal is to identify ONLY clear, actionable tasks that the recipient of this email needs to perform.

STRICT GUIDELINES:
1. Actionable Tasks Only: Only extract if there is something the user MUST DO (e.g., reply, sign, pay, attend, review).
2. Skip Informative Content: Do NOT extract tasks for newsletters, general updates, or informative receipts unless there's a specific follow-up required.
3. Specificity: The 'action_text' MUST be specific and professional (e.g., "Submit Project X report by EOD" instead of "Submit report").
4. Priority: If multiple tasks exist, extract the single most important one.
5. No Junk: If the email is clearly marketing or spam, set 'should_create_task' to false.

Respond with ONLY a JSON object:
{{
    "action_text": "Specific, concise action (plain text)",
    "deadline": "ISO format date (YYYY-MM-DDTHH:MM:SSZ) or null",
    "should_create_task": true/false
}}

Context:
Current UTC Time: {current_time}

Email Subject: {subject}
Email Body:
{body}
"""

class GeminiExtractor(GeminiService):
    """
    Extracts tasks and deadlines from emails using Gemini 2.0 Flash.
    """
    
    def __init__(self):
        super().__init__(model_name='gemini-3-flash-preview')
        
    def extract_task(self, subject: str, body: str) -> Optional[Dict]:
        """
        Identify a task and its deadline from email content.
        """
        # Preprocess body to remove HTML tags and noise
        from emails.utils.text_processing import preprocess_for_ai
        cleaned_body = preprocess_for_ai(body or "")
        current_time = datetime.utcnow().isoformat() + "Z"
        
        prompt = EXTRACTION_PROMPT.format(
            subject=subject or "(No Subject)",
            body=cleaned_body or "(Empty Body)",
            current_time=current_time
        )
        
        response_text = self.generate_content(prompt)
        if not response_text:
            return None
            
        try:
            return self._parse_response(response_text)
        except Exception as e:
            logger.error(f"Failed to parse task extraction result: {e}")
            return None

    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse structured task JSON from Gemini response."""
        try:
            text = response_text.strip()
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1])
            
            data = json.loads(text)
            
            # Basic validation
            if not isinstance(data, dict):
                return None
                
            return {
                'action_text': data.get('action_text', 'Action required'),
                'deadline': data.get('deadline'),
                'should_create_task': bool(data.get('should_create_task', False))
            }
        except Exception:
            return None
