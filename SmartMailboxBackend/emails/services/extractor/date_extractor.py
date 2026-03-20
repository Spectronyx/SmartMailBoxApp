"""
Deadline Extractor using dateparser.

This module extracts date/time information from natural language text.

Design Decision:
We use dateparser library which handles complex date expressions like:
- "tomorrow at 5 PM"
- "next Friday"
- "in 2 days"
- "by end of month"
- Absolute dates like "January 30, 2026"

Why dateparser?
- Robust handling of relative dates
- Multi-language support
- Timezone aware
- Well-tested library

Future Improvements:
- Could use transformer models (e.g., SUTime, BERT-based date extractors)
  for better context understanding
- Could extract multiple deadlines and prioritize based on context
"""

import dateparser
from datetime import datetime, timezone
from typing import Optional
import re


class DeadlineExtractor:
    """
    Extracts deadline dates from email text.
    """
    
    def __init__(self):
        """Initialize the deadline extractor."""
        # dateparser settings for better accuracy
        self.settings = {
            'PREFER_DATES_FROM': 'future',  # Assume dates are in the future
            'RELATIVE_BASE': datetime.now(timezone.utc),
            'RETURN_AS_TIMEZONE_AWARE': True,
            'TIMEZONE': 'UTC'
        }
    
    def extract_deadline(self, text: str) -> Optional[datetime]:
        """
        Extract the most relevant deadline from text.
        
        Args:
            text: Input text (email body or summary)
            
        Returns:
            datetime object or None if no deadline found
        """
        if not text:
            return None
        
        # Proactively clean HTML tags
        from emails.utils.text_processing import preprocess_for_ai
        text = preprocess_for_ai(text)
        
        # Common deadline indicators
        deadline_patterns = [
            r'deadline[:\s]+([^.!?]+)',
            r'due[:\s]+([^.!?]+)',
            r'by[:\s]+([^.!?]+)',
            r'before[:\s]+([^.!?]+)',
            r'submit.*?by[:\s]+([^.!?]+)',
            r'complete.*?by[:\s]+([^.!?]+)',
        ]
        
        potential_dates = []
        
        # First, try to find dates near deadline keywords
        for pattern in deadline_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group(1).strip()
                parsed_date = dateparser.parse(date_text, settings=self.settings)
                if parsed_date:
                    potential_dates.append(parsed_date)
        
        # If no dates found with keywords, scan the entire text
        if not potential_dates:
            # Split into sentences and try to parse each
            # Clean and truncate text to prevent dateparser recursion errors
            safe_text = text[:2000] 
            sentences = re.split(r'[.!?]\s+', safe_text)
            
            for sentence in sentences[:5]:  # Limit to first 5 sentences
                # Skip very long "sentences" that might trigger recursion
                if len(sentence) > 200:
                    continue
                parsed_date = dateparser.parse(sentence, settings=self.settings)
                if parsed_date:
                    potential_dates.append(parsed_date)
        
        # Return the earliest future date
        if potential_dates:
            # Filter out past dates
            now = datetime.now(timezone.utc)
            future_dates = [d for d in potential_dates if d > now]
            
            if future_dates:
                return min(future_dates)  # Return earliest
        
        return None
    
    def extract_with_context(self, text: str) -> dict:
        """
        Extract deadline along with surrounding context.
        
        Args:
            text: Input text
            
        Returns:
            Dict with 'deadline' and 'context_sentence'
        """
        deadline = self.extract_deadline(text)
        
        if not deadline:
            return {'deadline': None, 'context_sentence': None}
        
        # Find the sentence containing the deadline
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            parsed = dateparser.parse(sentence, settings=self.settings)
            if parsed and abs((parsed - deadline).total_seconds()) < 60:  # Within 1 minute
                return {
                    'deadline': deadline,
                    'context_sentence': sentence.strip()
                }
        
        return {'deadline': deadline, 'context_sentence': None}
