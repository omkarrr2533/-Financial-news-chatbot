import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class ImpactCalculator:
    def __init__(self):
        self.weights = {
            'mentions': 0.25,
            'sentiment': 0.30,
            'india_relevance': 0.25,
            'recency': 0.15,
            'source_credibility': 0.05
        }
        
        self.source_credibility = {
            'reuters.com': 1.0,
            'bloomberg.com': 1.0,
            'ft.com': 0.95,
            'economictimes.indiatimes.com': 0.90,
            'moneycontrol.com': 0.85,
            'AI Search': 0.95,
            'default': 0.70
        }
    
    def calculate_impact_scores(self, articles):
        """
        Calculate impact scores for all institutions based on articles
        Returns: dict of institution scores sorted by impact
        """
        institution_data = defaultdict(lambda: {
            'mentions': 0,
            'sentiment_scores': [],
            'india_relevance': 0,
            'articles': [],
            'recency_scores': [],
            'source_scores': []
        })
        
        # Aggregate data for each institution
        for article in articles:
            institutions = article.get('institutions', [])
            sentiment = article.get('sentiment_score', 0)
            india_relevance = article.get('india_relevance', 0)
            published_date = article.get('published_date')
            source = article.get('source', 'default')
            
            # Calculate recency score (decay over 48 hours)
            if isinstance(published_date, str):
                try:
                    published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                except:
                    published_date = datetime.now()
            elif not isinstance(published_date, datetime):
                published_date = datetime.now()
            
            hours_ago = (datetime.now() - published_date).total_seconds() / 3600
            recency_score = max(0, 1 - (hours_ago / 48))  # Linear decay over 48 hours
            
            # Get source credibility
            source_score = self._get_source_credibility(source)
            
            for institution in institutions:
                institution_data[institution]['mentions'] += 1
                institution_data[institution]['sentiment_scores'].append(sentiment)
                institution_data[institution]['india_relevance'] += india_relevance
                institution_data[institution]['articles'].append(article)
                institution_data[institution]['recency_scores'].append(recency_score)
                institution_data[institution]['source_scores'].append(source_score)
        
        # Calculate final impact scores
        impact_scores = {}
        
        for institution, data in institution_data.items():
            if data['mentions'] == 0:
                continue
            
            # Normalize metrics
            mentions_score = min(data['mentions'] / 10, 1.0)  # Cap at 10 mentions
            
            # Average sentiment (weighted by recency)
            sentiment_scores = np.array(data['sentiment_scores'])
            recency_weights = np.array(data['recency_scores'])
            avg_sentiment = np.average(sentiment_scores, weights=recency_weights) if len(sentiment_scores) > 0 else 0
            sentiment_score = (avg_sentiment + 1) / 2  # Normalize to 0-1
            
            # India relevance score (log scale to prevent domination)
            india_score = min(np.log1p(data['india_relevance']) / 5, 1.0)
            
            # Average recency
            recency_score = np.mean(data['recency_scores'])
            
            # Average source credibility
            credibility_score = np.mean(data['source_scores'])
            
            # Calculate weighted impact score (0-100 scale)
            impact = (
                mentions_score * self.weights['mentions'] +
                sentiment_score * self.weights['sentiment'] +
                india_score * self.weights['india_relevance'] +
                recency_score * self.weights['recency'] +
                credibility_score * self.weights['source_credibility']
            ) * 100
            
            # Determine sentiment direction
            if avg_sentiment > 0.1:
                direction = 'Positive'
            elif avg_sentiment < -0.1:
                direction = 'Negative'
            else:
                direction = 'Mixed'
            
            impact_scores[institution] = {
                'institution': institution,
                'impact_score': round(impact, 2),
                'mentions': data['mentions'],
                'sentiment': direction,
                'sentiment_value': round(avg_sentiment, 3),
                'india_linkage': data['india_relevance'],
                'recent_articles': len([a for a in data['articles'] if (datetime.now() - a.get('published_date', datetime.now())).total_seconds() / 3600 <= 24]),
                'key_drivers': self._extract_key_drivers(data['articles'][:3]),
                'articles': data['articles'][:5]  # Top 5 articles
            }
        
        # Sort by impact score
        sorted_scores = dict(sorted(impact_scores.items(), 
                                   key=lambda x: x[1]['impact_score'], 
                                   reverse=True))
        
        return sorted_scores
    
    def _get_source_credibility(self, source):
        """Get credibility score for a news source"""
        for key in self.source_credibility:
            if key in source.lower():
                return self.source_credibility[key]
        return self.source_credibility['default']
    
    def _extract_key_drivers(self, articles):
        """Extract key drivers from top articles"""
        drivers = []
        for article in articles[:3]:
            title = article.get('title', '')
            if title and len(title) > 20:
                # Extract key phrase (simplified)
                drivers.append(title[:80] + '...' if len(title) > 80 else title)
        
        return drivers[:3]
    
    def generate_summary(self, impact_scores):
        """Generate executive summary from impact scores"""
        if not impact_scores:
            return [
                "No significant financial news found in the last 48 hours",
                "Try adjusting the time range or check back later",
                "Markets may be experiencing low volatility"
            ]
        
        top_institutions = list(impact_scores.items())[:3]
        positive_count = sum(1 for _, data in impact_scores.items() if data['sentiment'] == 'Positive')
        negative_count = sum(1 for _, data in impact_scores.items() if data['sentiment'] == 'Negative')
        high_india_count = sum(1 for _, data in impact_scores.items() if data['india_linkage'] > 5)
        
        summary = []
        
        if top_institutions:
            top_name = top_institutions[0][0]
            top_score = top_institutions[0][1]['impact_score']
            summary.append(f"{top_name} leads with highest India market impact (Score: {top_score:.1f})")
        
        if positive_count > negative_count:
            summary.append(f"Market sentiment trending positive with {positive_count} institutions showing bullish signals")
        elif negative_count > positive_count:
            summary.append(f"Cautionary signals detected with {negative_count} institutions showing bearish trends")
        else:
            summary.append(f"Mixed market sentiment with balanced positive ({positive_count}) and negative ({negative_count}) signals")
        
        if high_india_count > 0:
            summary.append(f"Strong India focus detected in {high_india_count} major institutions")
        else:
            summary.append("Limited direct India-specific news; monitoring broader emerging market trends")
        
        return summary