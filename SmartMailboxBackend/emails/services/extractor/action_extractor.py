"""
Action Extractor using rule-based NLP.

This module detects actionable sentences in email text.

Design Decision:
We use a rule-based approach with action verb detection because:
1. **Fast**: No model inference required
2. **Explainable**: Easy to see which verbs triggered the match
3. **Customizable**: Easy to add domain-specific verbs

Limitations:
- May miss implicit actions ("Looking forward to your response")
- Cannot understand context ("Don't forget to NOT submit")
- No understanding of negation or conditional phrases

Future Improvements:
- Use transformer models (BERT, RoBERTa) for intent classification
- Implement Named Entity Recognition (NER) for better context
- Add dependency parsing to understand subject-verb-object relationships
- Use zero-shot classification for dynamic action detection
"""

import re
from typing import Optional, Dict


class ActionExtractor:
    """
    Extracts actionable text from emails using verb pattern matching.
    """
    
    # Action verbs that indicate tasks
    ACTION_VERBS = {
        'submit', 'apply', 'register', 'attend', 'join', 'complete',
        'pay', 'send', 'upload', 'download', 'review', 'approve',
        'sign', 'fill', 'respond', 'reply', 'confirm', 'rsvp',
        'prepare', 'finish', 'deliver', 'provide', 'update',
        'schedule', 'book', 'reserve', 'enroll', 'participate'
    }
    
    def __init__(self):
        """Initialize the action extractor."""
        # Compile regex pattern for action verbs
        verb_pattern = '|'.join(self.ACTION_VERBS)
        self.action_pattern = re.compile(
            rf'\b({verb_pattern})\b',
            re.IGNORECASE
        )
    
    def extract_action(self, text: str) -> Optional[str]:
        """
        Extract the most relevant action sentence.
        
        Args:
            text: Input text (email body or summary)
            
        Returns:
            Action text or None
        """
        if not text:
            return None
        
        # Proactively clean HTML if present
        from emails.utils.text_processing import preprocess_for_ai
        text = preprocess_for_ai(text)
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        # Score each sentence
        scored_sentences = []
        for sentence in sentences:
            score = self._score_sentence(sentence)
            if score > 0:
                scored_sentences.append((score, sentence))
        
        if not scored_sentences:
            return None
        
        # Return highest scoring sentence
        scored_sentences.sort(reverse=True)
        return scored_sentences[0][1]
    
    def extract_all_actions(self, text: str) -> list:
        """
        Extract all actionable sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of action sentences
        """
        if not text:
            return []
        
        sentences = self._split_sentences(text)
        actions = []
        
        for sentence in sentences:
            if self.action_pattern.search(sentence):
                actions.append(sentence)
        
        return actions
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        # Basic sentence splitting
        sentences = re.split(r'[.!?]\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentence(self, sentence: str) -> float:
        """
        Score a sentence based on action indicators.
        
        Higher score = more likely to be an actionable item
        """
        score = 0.0
        
        # Check for action verbs
        verb_matches = list(self.action_pattern.finditer(sentence))
        score += len(verb_matches) * 2.0  # Each verb adds 2 points
        
        # Boost for imperative mood (starts with verb)
        if verb_matches and sentence.lower().startswith(tuple(self.ACTION_VERBS)):
            score += 1.0
        
        # Boost for deadline keywords in same sentence
        deadline_keywords = ['by', 'before', 'deadline', 'due', 'until']
        for keyword in deadline_keywords:
            if re.search(rf'\b{keyword}\b', sentence, re.IGNORECASE):
                score += 1.5
        
        # Penalize questions (less likely to be actions)
        if '?' in sentence:
            score *= 0.3
        
        # Penalize very short sentences (< 5 words)
        word_count = len(sentence.split())
        if word_count < 5:
            score *= 0.5
        
        # Penalize very long sentences (> 30 words - might be too vague)
        if word_count > 30:
            score *= 0.7
        
        return score
    
    def extract_with_metadata(self, text: str) -> Dict:
        """
        Extract action with additional metadata.
        
        Args:
            text: Input text
            
        Returns:
            Dict with 'action', 'verbs_found', 'confidence'
        """
        action = self.extract_action(text)
        
        if not action:
            return {
                'action': None,
                'verbs_found': [],
                'confidence': 0.0
            }
        
        # Find which verbs were matched
        verbs_found = [m.group() for m in self.action_pattern.finditer(action)]
        
        # Calculate confidence (normalized score)
        score = self.score_sentence(action)
        max_possible_score = 10.0  # Rough maximum
        confidence = min(score / max_possible_score, 1.0)
        
        return {
            'action': action,
            'verbs_found': verbs_found,
            'confidence': confidence
        }
