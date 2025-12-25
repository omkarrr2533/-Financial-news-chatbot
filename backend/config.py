import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Server Settings
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/news_cache.db')
    
    # Refresh Intervals (in seconds)
    NEWS_REFRESH_INTERVAL = int(os.getenv('NEWS_REFRESH_INTERVAL', 1800))
    QUICK_REFRESH_INTERVAL = int(os.getenv('QUICK_REFRESH_INTERVAL', 300))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # News Sources
    NEWS_SOURCES = {
        'reuters': 'https://www.reuters.com/business/finance/',
        'bloomberg': 'https://www.bloomberg.com/markets',
        'ft': 'https://www.ft.com/global-economy',
        'economic_times': 'https://economictimes.indiatimes.com/markets',
        'moneycontrol': 'https://www.moneycontrol.com/news/business/markets/'
    }
    
    # RSS Feeds
    RSS_FEEDS = [
        'https://feeds.reuters.com/reuters/businessNews',
        'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'https://www.moneycontrol.com/rss/business.xml',
    ]
    
    # Financial Institutions to track
    FINANCIAL_INSTITUTIONS = [
        'JPMorgan', 'Goldman Sachs', 'Morgan Stanley', 'HSBC', 'Citigroup',
        'BlackRock', 'Vanguard', 'State Street', 'Fidelity', 'BNP Paribas',
        'Deutsche Bank', 'UBS', 'Credit Suisse', 'Barclays', 'Standard Chartered',
        'Bank of America', 'Wells Fargo', 'RBI', 'HDFC Bank', 'ICICI Bank',
        'Axis Bank', 'Kotak Mahindra', 'SBI', 'Yes Bank', 'IndusInd Bank'
    ]
    
    # India-specific keywords
    INDIA_KEYWORDS = [
        'India', 'Indian', 'RBI', 'Reserve Bank of India', 'Sensex', 'Nifty',
        'BSE', 'NSE', 'INR', 'rupee', 'Mumbai', 'SEBI', 'Modi', 'Delhi',
        'Bangalore', 'emerging markets', 'GIFT City', 'FPI', 'FDI',
        'Indian economy', 'Indian markets', 'Indian stocks'
    ]
    
    # Sentiment keywords
    POSITIVE_KEYWORDS = [
        'growth', 'profit', 'upgrade', 'investment', 'expansion', 'positive',
        'gains', 'optimistic', 'rally', 'surge', 'boom', 'bullish', 'outperform',
        'strong', 'robust', 'recovery', 'upbeat', 'accelerate', 'breakthrough'
    ]
    
    NEGATIVE_KEYWORDS = [
        'loss', 'decline', 'downgrade', 'concern', 'risk', 'negative',
        'falls', 'warning', 'crash', 'recession', 'bearish', 'weak',
        'slowdown', 'crisis', 'plunge', 'underperform', 'volatile', 'threat'
    ]
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required. Please set it in .env file")
        return True