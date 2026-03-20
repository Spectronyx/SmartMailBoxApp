"""
Email classification services package.

This package contains the email classification pipeline:
- rule_classifier: Rule-based classification
- ml_classifier: ML-based classification
- classifier_pipeline: Hybrid classification orchestrator
"""

from .classifier_pipeline import EmailClassifier, get_classifier

__all__ = ['EmailClassifier', 'get_classifier']
