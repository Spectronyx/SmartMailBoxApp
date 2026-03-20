"""
Frequency-based Extractive Summarizer.

This module implements a simple but effective summarization algorithm based on
word frequency scoring.
"""

from collections import Counter
import heapq
from .text_processor import TextProcessor


class FrequencySummarizer:
    """
    Summarizes text by selecting sentences with the highest scoring words.
    
    Algorithm:
    1. Calculate word frequencies (TF) for the whole document (ignoring stop words)
    2. Normalize frequencies by dividing by max frequency
    3. Score each sentence: sum of normalized frequencies of its words
    4. Return top N highest scoring sentences
    """
    
    def __init__(self, top_n_sentences: int = 3):
        """
        Initialize summarizer.
        
        Args:
            top_n_sentences: Number of sentences to include in summary
        """
        self.top_n = top_n_sentences
        self.processor = TextProcessor()
        self.stop_words = self.processor.get_stop_words()
    
    def summarize(self, text: str) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Input text
            
        Returns:
            Summary string (selected sentences joined by spaces)
        """
        if not text:
            return ""
            
        # 1. Preprocessing
        clean_text = self.processor.clean_text(text)
        sentences = self.processor.split_into_sentences(clean_text)
        
        # If text is too short, perform no summarization, just return it
        if len(sentences) <= self.top_n:
            return text
            
        # 2. Calculate Word Frequencies
        word_freq = Counter()
        for sentence in sentences:
            words = self.processor.tokenize(sentence)
            for word in words:
                if word not in self.stop_words:
                    word_freq[word] += 1
        
        # Normalize frequencies
        if not word_freq:
            return text  # No meaningful words found
            
        max_freq = max(word_freq.values())
        for word in word_freq:
            word_freq[word] /= max_freq
            
        # 3. Score Sentences
        sentence_scores = {}
        for sentence in sentences:
            words = self.processor.tokenize(sentence)
            # Sentence score = sum of word scores
            score = sum(word_freq.get(word, 0) for word in words)
            
            # Penalize very short sentences (< 4 words) as they lack context
            if len(words) < 4:
                score *= 0.5
                
            sentence_scores[sentence] = score
            
        # 4. Select Top N Sentences
        # Use heapq to find top N efficiently
        summary_sentences = heapq.nlargest(
            self.top_n, 
            sentence_scores, 
            key=sentence_scores.get
        )
        
        # Sort sentences by their appearance order in original text
        # (This is important for flow/coherence)
        sentence_order = {sent: i for i, sent in enumerate(sentences)}
        summary_sentences.sort(key=lambda s: sentence_order[s])
        
        return ' '.join(summary_sentences)
