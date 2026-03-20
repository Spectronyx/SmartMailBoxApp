"""
Email Classification Pipeline

This module orchestrates a three-tier classification approach:
1. Rule-based classification (fast, deterministic, no API needed)
2. Gemini AI classification (smart, context-aware, needs API key)
3. ML-based classification (offline fallback using TF-IDF + LogReg)

Design Decision: Three-Tier Fallback
- **Rules first**: Catches obvious patterns instantly (spam, critical keywords)
- **Gemini second**: Understands nuance and context for ambiguous emails
- **ML fallback**: Works offline when Gemini API is unavailable

This ensures the system always returns a classification, even without
internet access or API credits.
"""

import logging
from typing import Dict, Optional
from .rule_classifier import RuleBasedClassifier
from .ml_classifier import MLClassifier
from .gemini_classifier import GeminiClassifier

logger = logging.getLogger(__name__)


class EmailClassifier:
    """
    Hybrid email classifier combining rules and ML.
    
    This is the main interface for email classification in the application.
    """
    
    def __init__(self):
        """Initialize all three classifier tiers."""
        self.rule_classifier = RuleBasedClassifier()
        self.gemini_classifier = GeminiClassifier()
        self.ml_classifier = MLClassifier()
    
    def classify(self, sender: str, subject: str, body: str) -> Dict[str, any]:
        """
        Classify an email using hybrid approach.
        
        Args:
            sender: Email sender address
            subject: Email subject line
            body: Email body content
            
        Returns:
            Dictionary with classification results:
            {
                'category': str,
                'method': 'rule' or 'ml',
                'confidence': float (for ML) or None (for rules),
                'matched_patterns': list (for rules) or None (for ML)
            }
        """
        # Step 1: Try rule-based classification (fastest, no API needed)
        try:
            rule_category = self.rule_classifier.classify(sender, subject, body)
            
            if rule_category != 'UNKNOWN':
                matched = self.rule_classifier.get_matched_patterns(sender, subject, body)
                logger.info(f"Rule-based classified '{subject[:40]}' as {rule_category}")
                return {
                    'category': rule_category,
                    'method': 'rule',
                    'confidence': None,
                    'matched_patterns': matched['patterns']
                }
        except Exception as e:
            logger.error(f"Error in rule-based classification: {str(e)}")
            # Continue to next tier
        
        # Step 2: Try Gemini AI classification (smart, context-aware)
        try:
            gemini_result = self.gemini_classifier.classify(sender, subject, body)
            
            if gemini_result:
                logger.info(f"Gemini classified '{subject[:40]}' as {gemini_result['category']}")
                return {
                    'category': gemini_result['category'],
                    'method': 'gemini',
                    'confidence': gemini_result.get('confidence'),
                    'matched_patterns': None,
                    'reason': gemini_result.get('reason')
                }
        except Exception as e:
            logger.error(f"Error in Gemini classification: {str(e)}")
            # Continue to next tier
        
        # Step 3: ML fallback (works offline, no API needed)
        try:
            combined_text = f"{subject} {body}"
            ml_category, confidence = self.ml_classifier.classify_with_confidence(combined_text)
            logger.info(f"ML fallback classified '{subject[:40]}' as {ml_category}")
            
            return {
                'category': ml_category,
                'method': 'ml',
                'confidence': round(confidence, 3),
                'matched_patterns': None
            }
        except Exception as e:
            logger.error(f"Error in ML classification: {str(e)}")
            # Final fallback if everything fails
            return {
                'category': 'INFO',
                'method': 'fallback_default',
                'confidence': 0.0,
                'matched_patterns': None,
                'note': 'All classification tiers failed'
            }
    
    def classify_batch(self, emails: list) -> list:
        """
        Classify multiple emails efficiently.
        
        Args:
            emails: List of dicts with 'sender', 'subject', 'body' keys
            
        Returns:
            List of classification results
        """
        results = []
        for email in emails:
            result = self.classify(
                email.get('sender', ''),
                email.get('subject', ''),
                email.get('body', '')
            )
            results.append(result)
        
        return results
    
    def retrain_ml_model(self):
        """
        Retrain the ML model.
        
        This can be called when new training data is available.
        In production, this would use real labeled emails.
        """
        self.ml_classifier.train_model()


# Singleton instance for reuse across requests
_classifier_instance = None


def get_classifier() -> EmailClassifier:
    """
    Get or create the singleton classifier instance.
    
    Design Decision: Using a singleton to avoid reloading
    the ML model on every request (expensive operation).
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = EmailClassifier()
    return _classifier_instance
