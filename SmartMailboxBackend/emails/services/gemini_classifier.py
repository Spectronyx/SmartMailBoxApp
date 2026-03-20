import logging
import json
from typing import Dict, Optional
from .gemini_base import GeminiService

logger = logging.getLogger(__name__)

# The classification prompt
CLASSIFICATION_PROMPT = """You are an email classification AI. Classify the following email into EXACTLY ONE of these categories:

- CRITICAL: Urgent emails requiring immediate action (deadlines, emergencies, important meetings, legal notices, security alerts)
- OPPORTUNITY: Beneficial emails (job offers, business proposals, networking, useful promotions, collaboration requests)
- INFO: Informational emails (newsletters, updates, confirmations, receipts, general correspondence)
- JUNK: Unwanted emails (spam, mass marketing, phishing attempts, irrelevant promotions)

Respond with ONLY a JSON object in this exact format (no markdown, no explanation):
{{"category": "CRITICAL", "confidence": 0.95, "reason": "Brief reason"}}

Email Subject: {subject}
Email Body:
{body}
"""


class GeminiClassifier(GeminiService):
    """
    Classifies emails using the Gemini 3 Flash model.
    """
    
    VALID_CATEGORIES = {'CRITICAL', 'OPPORTUNITY', 'INFO', 'JUNK'}
    
    def __init__(self):
        # Migrated from gemini-2.0-flash to gemini-3-flash-preview
        super().__init__(model_name='gemini-3-flash-preview')
    
    def classify(self, sender: str, subject: str, body: str) -> Optional[Dict]:
        """
        Classify an email using Gemini 3 reasoning.
        """
        # Preprocess body to remove HTML tags and noise
        from emails.utils.text_processing import preprocess_for_ai
        cleaned_body = preprocess_for_ai(body or "")
        
        prompt = CLASSIFICATION_PROMPT.format(
            subject=subject or "(No Subject)",
            body=cleaned_body or "(Empty Body)"
        )
        
        # We pass additional configuration for the Gemini 3 thinking engine
        extra_config = {
            "thinking_level": "high", 
            "temperature": 0.7  # Balanced for structured JSON output
        }
        
        # Ensure your base class generate_content accepts **kwargs
        response_text = self.generate_content(prompt, **extra_config)
        
        if not response_text:
            return None
            
        try:
            result = self._parse_response(response_text)
            if result:
                logger.debug(f"Gemini 3 classified '{subject[:30]}...' as {result['category']}")
            return result
        except Exception as e:
            logger.error(f"Failed to parse classification: {e}")
            return None

    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse structured JSON from Gemini response."""
        try:
            text = response_text.strip()
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1])
            
            data = json.loads(text)
            category = data.get('category', '').upper()
            if category not in self.VALID_CATEGORIES:
                return None
            
            return {
                'category': category,
                'confidence': float(data.get('confidence', 0.8)),
                'reason': data.get('reason', 'Classified by Gemini 3.0')
            }
        except Exception:
            return None