"""
Gemini-Powered Email Summarizer.

Uses Gemini 2.0 Flash for abstractive, high-quality email summarization.
"""

import logging
from typing import Optional
from ..gemini_base import GeminiService

logger = logging.getLogger(__name__)

SUMMARIZATION_PROMPT = """You are an expert email assistant. Summarize the following email in a concise, professional manner as plain text WITHOUT any HTML tags.

Guidelines:
- Maintain the original tone (e.g., urgent, formal, casual).
- Highlight key actions, deadlines, and the main point.
- Keep the summary under 3-4 sentences.
- Avoid preamble (e.g., "The email says...", "This is a summary of...").

Email Subject: {subject}
Email Body:
{body}
"""

class GeminiSummarizer(GeminiService):
    """
    Summarizes emails using Gemini 2.0 Flash.
    """
    
    def __init__(self):
        super().__init__(model_name='gemini-3.0-flash')
        
    def summarize(self, subject: str, body: str, is_cleaned: bool = False) -> Optional[str]:
        """
        Generate an abstractive summary of an email.
        """
        if not is_cleaned:
            # Preprocess body to remove HTML tags and noise
            from emails.utils.text_processing import preprocess_for_ai
            cleaned_body = preprocess_for_ai(body or "")
        else:
            cleaned_body = body
            
        prompt = SUMMARIZATION_PROMPT.format(
            subject=subject or "(No Subject)",
            body=cleaned_body or "(Empty Body)"
        )
        
        summary = self.generate_content(prompt)
        if summary:
            logger.debug(f"Gemini summarized email '{subject[:30]}...'")
            return summary.strip()
            
        return None
