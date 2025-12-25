from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import sys
import os
# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import Config

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.config = Config()
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment using multiple methods and return aggregated score
        Returns: dict with sentiment score, label, and confidence
        """
        if not text:
            return {'score': 0, 'label': 'Neutral', 'confidence': 0}
        
        # VADER sentiment analysis
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity
        
        # Keyword-based sentiment
        keyword_score = self._keyword_sentiment(text)
        
        # Weighted average (VADER is generally more accurate for news)
        final_score = (vader_compound * 0.5) + (textblob_score * 0.3) + (keyword_score * 0.2)
        
        # Determine label
        if final_score > 0.05:
            label = 'Positive'
        elif final_score < -0.05:
            label = 'Negative'
        else:
            label = 'Mixed'
        
        # Confidence (based on agreement between methods)
        confidence = self._calculate_confidence(vader_compound, textblob_score, keyword_score)
        
        return {
            'score': round(final_score, 3),
            'label': label,
            'confidence': round(confidence, 2),
            'vader': round(vader_compound, 3),
            'textblob': round(textblob_score, 3),
            'keyword': round(keyword_score, 3)
        }
    
    def _keyword_sentiment(self, text):
        """Calculate sentiment based on keyword matching"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.config.POSITIVE_KEYWORDS 
                            if word.lower() in text_lower)
        negative_count = sum(1 for word in self.config.NEGATIVE_KEYWORDS 
                            if word.lower() in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0
        
        # Normalize to -1 to 1 range
        return (positive_count - negative_count) / total
    
    def _calculate_confidence(self, vader, textblob, keyword):
        """Calculate confidence based on agreement between methods"""
        scores = [vader, textblob, keyword]
        
        # Check if all scores agree on direction
        positive_count = sum(1 for s in scores if s > 0.05)
        negative_count = sum(1 for s in scores if s < -0.05)
        
        if positive_count == 3 or negative_count == 3:
            return 0.95  # High confidence
        elif positive_count == 2 or negative_count == 2:
            return 0.75  # Medium confidence
        else:
            return 0.50  # Low confidence
    
    def extract_institutions(self, text):
        """Extract mentioned financial institutions from text"""
        institutions_found = []
        
        for institution in self.config.FINANCIAL_INSTITUTIONS:
            pattern = re.compile(r'\b' + re.escape(institution) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                institutions_found.append(institution)
        
        return institutions_found
    
    def calculate_india_relevance(self, text):
        """Calculate how relevant the text is to Indian markets"""
        text_lower = text.lower()
        
        relevance_score = 0
        for keyword in self.config.INDIA_KEYWORDS:
            count = text_lower.count(keyword.lower())
            relevance_score += count
        
        return relevance_score