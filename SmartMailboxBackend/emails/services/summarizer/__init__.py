"""
Email summarization services.

This package provides tools for generating extractive summaries of email content.
"""

from .pipeline import SummarizerPipeline
from .frequency_summarizer import FrequencySummarizer

# Expose main classes
__all__ = ['SummarizerPipeline', 'FrequencySummarizer']
