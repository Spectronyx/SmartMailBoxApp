"""
Text utility functions for summarization.

This module provides cleaning and tokenization utilities.
"""

import re
import string


class TextProcessor:
    """
    Handles text cleaning and preprocessing for summarization.
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean the input text by removing extra whitespace and special chars.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Replace multiple newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove [brackets] content which is often meta-info
        text = re.sub(r'\[.*?\]', '', text)
        
        return text.strip()
    
    @staticmethod
    def split_into_sentences(text: str) -> list:
        """
        Split text into sentences.
        
        Design Decision: Simple regex splitting is used here for simplicity.
        In a production NLP pipeline, we might use NLTK or spaCy's sentence tokenizer
        for better handling of abbreviations (Mr., Dr., etc.).
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Split by ., !, ? followed by a space or end of string
        # This is a basic implementation but works for most emails
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter out empty strings
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def tokenize(sentence: str) -> list:
        """
        Tokenize a sentence into words.
        
        Args:
            sentence: Input sentence
            
        Returns:
            List of lowercase words
        """
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        clean_sentence = sentence.translate(translator)
        
        # Split and convert to lowercase
        return [word.lower() for word in clean_sentence.split() if word]
    
    @staticmethod
    def get_stop_words() -> set:
        """
        Return a set of common English stop words.
        
        Design Decision: Hardcoded list to avoid huge NLTK dependency just for this.
        """
        return {
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then',
            'just', 'so', 'than', 'such', 'both',
            'through', 'about', 'for', 'is', 'of', 'while', 'during', 'to',
            'from', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'can', 'will', 'just', 'should', 'now', 'are', 'was', 'were', 'have',
            'has', 'had', 'do', 'does', 'did', 'be', 'been', 'being', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their', 'yours',
            'please', 'thanks', 'thank', 'sincerely', 'regards', 'best', 'hi', 'hello',
            'dear'  # Common email words
        }
