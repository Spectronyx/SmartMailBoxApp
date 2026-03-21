"""
Summarization Pipeline Orchestrator.

This module manages the flow of email summarization, including validation
and integration with the summarizer algorithm.
"""

from typing import Dict, Optional, List
from .frequency_summarizer import FrequencySummarizer
from .gemini_summarizer import GeminiSummarizer


class SummarizerPipeline:
    """
    Orchestrates email summarization.
    
    Responsibilities:
    1. Validation (is email long enough?)
    2. Runs the summarization algorithm
    3. Error handling
    
    Design Decision:
    We use a frequency-based extractive summarizer for Sprint 3.
    This class is designed to be easily extensible to support abstractive
    summarization (LLMs) in the future by swapping the internal summarizer.
    """
    
    def __init__(self, min_length: int = 50, top_n: int = 3):
        """
        Initialize the pipeline.
        
        Args:
            min_length: Minimum character count to justify summarization
            top_n: Number of sentences in summary
        """
        self.min_length = min_length
        self.summarizer = FrequencySummarizer(top_n_sentences=top_n)
        self.gemini_summarizer = GeminiSummarizer()
    
    def process(self, email_body: str, email_subject: str = "") -> Optional[str]:
        """
        Generate a summary for an email.
        """
        if not email_body:
            return None
            
        # 1. Clean the body once at the pipeline level (removes HTML, CSS, script, etc.)
        from emails.utils.text_processing import preprocess_for_ai
        cleaned_body = preprocess_for_ai(email_body)
        
        if len(cleaned_body) < self.min_length:
            return None  # Too short to summarize
            
        try:
            # 2. Try Gemini first (Abstractive)
            # Pass original body to gemini_summarizer (which does its own cleaning or might want full context)
            # Actually, better to pass cleaned body to ensure no CSS leakage.
            summary = self.gemini_summarizer.summarize(email_subject, cleaned_body, is_cleaned=True)
            
            # 3. Fallback to Frequency (Extractive)
            if not summary:
                summary = self.summarizer.summarize(cleaned_body)
            
            # If summary is basically the whole text (short text), don't return it
            if summary and len(summary) >= len(cleaned_body) * 0.9:
                return None
                
            return summary
            
        except Exception as e:
            # Log error in production
            return None
    
    def process_batch(self, emails: List[Dict[str, str]]) -> List[Dict]:
        """
        Process a batch of emails.
        
        Args:
            emails: List of dicts with 'id' and 'body'
            
        Returns:
            List of results with 'id' and 'summary'
        """
        results = []
        for email in emails:
            summary = self.process(
                email.get('body', ''),
                email.get('subject', '')
            )
            if summary:
                results.append({
                    'id': email['id'],
                    'summary': summary
                })
        return results


# Singleton instance
_pipeline_instance = None


def get_summarizer_pipeline() -> SummarizerPipeline:
    """Get or create singleton pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = SummarizerPipeline()
    return _pipeline_instance
