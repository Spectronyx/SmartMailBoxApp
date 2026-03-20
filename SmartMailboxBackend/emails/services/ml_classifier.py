"""
ML-based Email Classifier

This module implements machine learning-based email classification using:
- TF-IDF vectorization for text features
- Logistic Regression for classification

Design Decision: We use Logistic Regression because:
1. Works well with TF-IDF features
2. Provides probability scores (useful for confidence thresholds)
3. Fast training and prediction
4. Interpretable (can inspect feature weights)

Future Improvements:
- Use a larger, real-world training dataset
- Experiment with other models (Naive Bayes, SVM, Neural Networks)
- Add hyperparameter tuning
- Implement cross-validation
- Use pre-trained embeddings (BERT, etc.)
"""

import os
import joblib
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from typing import Tuple, List


class MLClassifier:
    """
    ML-based email classifier using TF-IDF + Logistic Regression.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the ML classifier.
        
        Args:
            model_path: Path to save/load the trained model
        """
        if model_path is None:
            # Default path: emails/services/models/
            base_dir = Path(__file__).parent
            model_dir = base_dir / 'models'
            model_dir.mkdir(exist_ok=True)
            model_path = str(model_dir / 'email_classifier.pkl')
        
        self.model_path = model_path
        self.model = None
        self.categories = ['CRITICAL', 'OPPORTUNITY', 'INFO', 'JUNK']
        
        # Try to load existing model
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            # Train a new model with sample data
            self.train_model()
    
    def _get_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Generate sample training data for email classification.
        
        Design Decision: Embedded training data for simplicity.
        In production, this should be replaced with a real dataset
        from labeled emails or external sources.
        
        Returns:
            Tuple of (texts, labels)
        """
        texts = [
            # CRITICAL examples
            "Urgent: Project deadline is tomorrow at 5 PM",
            "ASAP: Need your submission for the quarterly report",
            "Exam schedule has been released - check immediately",
            "Action required: Complete your assignment by Friday",
            "Important: System maintenance tonight - backup your data",
            "Deadline reminder: Tax filing due next week",
            "Critical bug in production - need immediate fix",
            "Emergency meeting scheduled for 3 PM today",
            "Your account will be suspended if payment not received",
            "Final notice: Submit your documents by end of day",
            
            # OPPORTUNITY examples
            "Exciting internship opportunity at Google",
            "We're hiring for a Senior Software Engineer position",
            "Job opening: Data Scientist role at our company",
            "Career opportunity: Join our team as Product Manager",
            "Interview invitation for the Backend Developer role",
            "Recruiting for Summer 2026 internship program",
            "New position available: Full Stack Engineer",
            "Opportunity to work on cutting-edge AI projects",
            "Join our startup as a founding engineer",
            "Exclusive job opportunity matching your profile",
            
            # INFO examples
            "Weekly team meeting notes and action items",
            "Project update: We completed phase 1 successfully",
            "FYI: New company policy on remote work",
            "Sharing the presentation from yesterday's meeting",
            "Monthly newsletter: Company updates and achievements",
            "Information: Office will be closed on Monday",
            "Update on the new feature release timeline",
            "Reminder: Team lunch next Friday at noon",
            "Summary of Q4 performance metrics",
            "Documentation for the new API is now available",
            
            # JUNK examples
            "Unsubscribe from our mailing list anytime",
            "Special promotion: 50% off on all items",
            "Newsletter: Top 10 tech trends this week",
            "Marketing update: New products launched",
            "No-reply: Your subscription has been confirmed",
            "Promotional offer: Limited time discount",
            "Weekly digest from noreply@example.com",
            "Advertisement: Best deals on electronics",
            "Spam: You've won a million dollars",
            "Unsubscribe link at the bottom of this email",
            
            # Additional CRITICAL examples
            "Immediate action needed on security breach",
            "Urgent submission required for compliance",
            "Exam results will be published tomorrow",
            "Critical system alert: Database connection failed",
            "Deadline approaching: Project proposal due soon",
            
            # Additional OPPORTUNITY examples
            "Freelance opportunity for Python developers",
            "Part-time job opening for students",
            "Internship application deadline extended",
            "Career fair invitation: Meet top employers",
            "Hiring event: Tech companies recruiting",
            
            # Additional INFO examples
            "Meeting minutes from the board discussion",
            "New employee onboarding schedule",
            "Updated contact list for the team",
            "Resource sharing: Useful development tools",
            "Announcement: New office location",
            
            # Additional JUNK examples
            "Promotional email from marketing team",
            "Newsletter subscription confirmation",
            "Automated message: Do not reply",
            "Marketing campaign: Summer sale",
            "Bulk email: Event invitation",
        ]
        
        labels = [
            # CRITICAL (10)
            'CRITICAL', 'CRITICAL', 'CRITICAL', 'CRITICAL', 'CRITICAL',
            'CRITICAL', 'CRITICAL', 'CRITICAL', 'CRITICAL', 'CRITICAL',
            
            # OPPORTUNITY (10)
            'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY',
            'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY',
            
            # INFO (10)
            'INFO', 'INFO', 'INFO', 'INFO', 'INFO',
            'INFO', 'INFO', 'INFO', 'INFO', 'INFO',
            
            # JUNK (10)
            'JUNK', 'JUNK', 'JUNK', 'JUNK', 'JUNK',
            'JUNK', 'JUNK', 'JUNK', 'JUNK', 'JUNK',
            
            # Additional examples (20)
            'CRITICAL', 'CRITICAL', 'CRITICAL', 'CRITICAL', 'CRITICAL',
            'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY', 'OPPORTUNITY',
            'INFO', 'INFO', 'INFO', 'INFO', 'INFO',
            'JUNK', 'JUNK', 'JUNK', 'JUNK', 'JUNK',
        ]
        
        return texts, labels
    
    def train_model(self):
        """
        Train the ML model on sample data.
        
        Design Decision: We use a Pipeline to combine:
        1. TF-IDF Vectorizer: Converts text to numerical features
        2. Logistic Regression: Multi-class classification
        
        The pipeline ensures consistent preprocessing during training and prediction.
        """
        print("Training ML classifier...")
        
        # Get training data
        texts, labels = self._get_training_data()
        
        # Create pipeline
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=500,  # Limit vocabulary size
                ngram_range=(1, 2),  # Use unigrams and bigrams
                stop_words='english',  # Remove common words
                min_df=1,  # Minimum document frequency
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,
                multi_class='multinomial',
                random_state=42
            ))
        ])
        
        # Train the model
        self.model.fit(texts, labels)
        
        # Save the model
        self.save_model()
        
        print(f"ML classifier trained and saved to {self.model_path}")
    
    def save_model(self):
        """Save the trained model to disk."""
        joblib.dump(self.model, self.model_path)
    
    def load_model(self):
        """Load a trained model from disk."""
        self.model = joblib.load(self.model_path)
        print(f"ML classifier loaded from {self.model_path}")
    
    def classify(self, text: str) -> str:
        """
        Classify an email using the ML model.
        
        Args:
            text: Combined email text (subject + body)
            
        Returns:
            Predicted category: CRITICAL, OPPORTUNITY, INFO, or JUNK
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        prediction = self.model.predict([text])[0]
        return prediction
    
    def classify_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Classify an email and return confidence score.
        
        Args:
            text: Combined email text (subject + body)
            
        Returns:
            Tuple of (predicted_category, confidence_score)
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        prediction = self.model.predict([text])[0]
        probabilities = self.model.predict_proba([text])[0]
        confidence = max(probabilities)
        
        return prediction, confidence
