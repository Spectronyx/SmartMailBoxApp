"""
Rule-based Email Classifier

This module implements deterministic rule-based classification for emails.
Rules are applied based on patterns in sender, subject, and body.

Design Decision: Rule-based classification is fast and deterministic,
making it ideal for obvious patterns like newsletters or urgent emails.
This reduces the load on the ML model and provides explainable results.
"""

import re
from typing import Optional


class RuleBasedClassifier:
    """
    Classifies emails using pattern matching rules.
    
    Returns one of: CRITICAL, OPPORTUNITY, JUNK, UNKNOWN
    """
    
    # Pattern definitions for each category
    JUNK_PATTERNS = [
        r'\bnewsletter\b',
        r'\bnoreply\b',
        r'\bno-reply\b',
        r'\bunsubscribe\b',
        r'\bpromotion\b',
        r'\bmarketing\b',
    ]
    
    CRITICAL_PATTERNS = [
        r'\burgent\b',
        r'\bdeadline\b',
        r'\bexam\b',
        r'\bsubmission\b',
        r'\bimmediate\b',
        r'\basap\b',
        r'\baction required\b',
        r'\bdue date\b',
    ]
    
    OPPORTUNITY_PATTERNS = [
        r'\binternship\b',
        r'\bhiring\b',
        r'\bopportunity\b',
        r'\bjob opening\b',
        r'\bcareer\b',
        r'\brecruiting\b',
        r'\binterview\b',
    ]
    
    def __init__(self):
        """Initialize the rule-based classifier with compiled regex patterns."""
        self.junk_regex = self._compile_patterns(self.JUNK_PATTERNS)
        self.critical_regex = self._compile_patterns(self.CRITICAL_PATTERNS)
        self.opportunity_regex = self._compile_patterns(self.OPPORTUNITY_PATTERNS)
    
    def _compile_patterns(self, patterns: list) -> re.Pattern:
        """
        Compile a list of patterns into a single regex.
        
        Args:
            patterns: List of regex pattern strings
            
        Returns:
            Compiled regex pattern
        """
        combined = '|'.join(patterns)
        return re.compile(combined, re.IGNORECASE)
    
    def classify(self, sender: str, subject: str, body: str) -> str:
        """
        Classify an email based on rules.
        
        Args:
            sender: Email sender address
            subject: Email subject line
            body: Email body content
            
        Returns:
            Category: CRITICAL, OPPORTUNITY, JUNK, or UNKNOWN
            
        Design Decision: We check in order of priority:
        1. JUNK (to filter out noise first)
        2. CRITICAL (high priority)
        3. OPPORTUNITY (medium priority)
        4. UNKNOWN (fallback to ML)
        """
        # Combine all text for pattern matching
        combined_text = f"{sender} {subject} {body}".lower()
        
        # Check JUNK patterns (newsletters, noreply, etc.)
        if self.junk_regex.search(combined_text):
            return 'JUNK'
        
        # Check CRITICAL patterns (urgent, deadline, etc.)
        if self.critical_regex.search(combined_text):
            return 'CRITICAL'
        
        # Check OPPORTUNITY patterns (internship, hiring, etc.)
        if self.opportunity_regex.search(combined_text):
            return 'OPPORTUNITY'
        
        # No rules matched - return UNKNOWN for ML classification
        return 'UNKNOWN'
    
    def get_matched_patterns(self, sender: str, subject: str, body: str) -> dict:
        """
        Get which patterns matched for debugging/explanation.
        
        Args:
            sender: Email sender address
            subject: Email subject line
            body: Email body content
            
        Returns:
            Dictionary with category and matched patterns
        """
        combined_text = f"{sender} {subject} {body}".lower()
        
        matched = {
            'category': 'UNKNOWN',
            'patterns': []
        }
        
        if self.junk_regex.search(combined_text):
            matched['category'] = 'JUNK'
            matched['patterns'] = [p for p in self.JUNK_PATTERNS 
                                  if re.search(p, combined_text, re.IGNORECASE)]
        elif self.critical_regex.search(combined_text):
            matched['category'] = 'CRITICAL'
            matched['patterns'] = [p for p in self.CRITICAL_PATTERNS 
                                  if re.search(p, combined_text, re.IGNORECASE)]
        elif self.opportunity_regex.search(combined_text):
            matched['category'] = 'OPPORTUNITY'
            matched['patterns'] = [p for p in self.OPPORTUNITY_PATTERNS 
                                  if re.search(p, combined_text, re.IGNORECASE)]
        
        return matched
