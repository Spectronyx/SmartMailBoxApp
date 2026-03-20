"""
Deadline and action extraction services.

This package provides tools for extracting actionable tasks from emails.
"""

from .pipeline import ExtractionPipeline, get_extraction_pipeline

__all__ = ['ExtractionPipeline', 'get_extraction_pipeline']
