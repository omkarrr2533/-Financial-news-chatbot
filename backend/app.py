from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.news_scraper import NewsScraper
from backend.sentiment_analyzer import SentimentAnalyzer
from backend.impact_calculator import ImpactCalculator
from backend.database import Database
from backend.config import Config

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')

app.config['SECRET_KEY'] = Config.SECRET_KEY

# CORS configuration (restrict in production)
allowed_origins = ["http://localhost:5000", "http://127.0.0.1:5000"]
if Config.DEBUG:
    allowed_origins.append("*")

CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

# Initialize components
db = Database()
scraper = NewsScraper()
sentiment_analyzer = SentimentAnalyzer()
impact_calculator = ImpactCalculator()

# Global cache
news_cache = {
    'last_update': None,
    'data': None,
    'is_processing': False
}

def process_and_analyze_news():
    """Main function to fetch, process, and analyze news"""
    global news_cache
    
    if news_cache['is_processing']:
        logger.warning("News processing already in progress, skipping...")
        return None
    
    news_cache['is_processing'] = True
    
    logger.info("="*50)
    logger.info(f"Starting news analysis at {datetime.now()}")
    logger.info("="*50)
    
    try:
        # 1. Fetch articles
        logger.info("Step 1: Fetching articles...")
        articles = scraper.comprehensive_search()
        logger.info(f"✓ Fetched {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles fetched")
            return None
        
        # 2. Analyze sentiment and extract data
        logger.info("Step 2: Analyzing sentiment...")
        processed_articles = []
        
        for article in articles:
            try:
                content = article.get('content', '') + ' ' + article.get('title', '')
                
                # Sentiment analysis
                sentiment = sentiment_analyzer.analyze_sentiment(content)
                
                # Extract institutions
                institutions = sentiment_analyzer.extract_institutions(content)
                
                # India relevance
                india_relevance = sentiment_analyzer.calculate_india_relevance(content)
                
                article['sentiment_score'] = sentiment['score']
                article['sentiment_label'] = sentiment['label']
                article['institutions'] = institutions
                article['india_relevance'] = india_relevance
                
                processed_articles.append(article)
                
                # Save to database
                db.insert_article(article)
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        logger.info(f"✓ Analyzed sentiment for {len(processed_articles)} articles")
        
        # 3. Calculate impact scores
        logger.info("Step 3: Calculating impact scores...")
        impact_scores = impact_calculator.calculate_impact_scores(processed_articles)
        logger.info(f"✓ Calculated scores for {len(impact_scores)} institutions")
        
        # 4. Generate summary
        logger.info("Step 4: Generating summary...")
        summary = impact_calculator.generate_summary(impact_scores)
        
        # 5. Prepare response
        top_10 = dict(list(impact_scores.items())[:10])
        
        # Calculate additional stats
        positive_count = sum(1 for data in top_10.values() if data['sentiment'] == 'Positive')
        negative_count = sum(1 for data in top_10.values() if data['sentiment'] == 'Negative')
        
        result = {
            'institutions': top_10,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(processed_articles),
            'total_institutions': len(impact_scores),
            'positive_count': positive_count,
            'negative_count': negative_count
        }
        
        # Update cache
        news_cache['last_update'] = datetime.now()
        news_cache['data'] = result
        
        # Save to database
        db.save_institution_scores(impact_scores)
        
        logger.info("✓ Analysis complete!")
        logger.info("="*50)
        
        # Emit update to connected clients
        try:
            socketio.emit('news_update', result)
        except Exception as e:
            logger.error(f"Error emitting update: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}", exc_info=True)
        return None
    finally:
        news_cache['is_processing'] = False

# Routes
@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest news analysis"""
    try:
        # If cache is recent (< 5 minutes), return cached data
        if news_cache['last_update'] and news_cache['data']:
            time_diff = (datetime.now() - news_cache['last_update']).total_seconds()
            if time_diff < 300:  # 5 minutes
                logger.info("Returning cached data")
                return jsonify({
                    'success': True,
                    'data': news_cache['data'],
                    'cache': True
                })
        
        # Otherwise, fetch fresh data
        logger.info("Fetching fresh data")
        result = process_and_analyze_news()
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'cache': False
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch news'
            }), 500
    except Exception as e:
        logger.error(f"Error in get_news: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_news():
    """Force refresh news data"""
    try:
        logger.info("Manual refresh requested")
        result = process_and_analyze_news()
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to refresh news'
            }), 500
    except Exception as e:
        logger.error(f"Error in refresh_news: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'last_update': news_cache['last_update'].isoformat() if news_cache['last_update'] else None,
        'cached_data': news_cache['data'] is not None,
        'is_processing': news_cache['is_processing']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        # Get current news data
        current_data = news_cache.get('data')
        
        if not current_data:
            return jsonify({
                'success': True,
                'response': "I don't have any news data loaded yet. Please click the 'Refresh Data' button first."
            })
        
        # Generate chatbot response
        response = generate_chatbot_response(user_message, current_data)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred processing your request'
        }), 500

def generate_chatbot_response(message, data):
    """Generate chatbot response based on user query"""
    message_lower = message.lower()
    institutions = data.get('institutions', {})
    
    # Check for specific institution queries
    for inst_name, inst_data in institutions.items():
        if inst_name.lower() in message_lower:
            return f"""📊 **{inst_name}** Analysis:
            
- **Impact Score**: {inst_data['impact_score']}
- **Sentiment**: {inst_data['sentiment']} ({inst_data['sentiment_value']})
- **Mentions**: {inst_data['mentions']} articles
- **India Linkage**: {inst_data['india_linkage']} references
- **Recent Activity**: {inst_data['recent_articles']} articles in last 24h

**Key Drivers**: {', '.join(inst_data['key_drivers'][:2]) if inst_data['key_drivers'] else 'No specific drivers identified'}"""
    
    # General queries
    if 'top' in message_lower or 'best' in message_lower or 'highest' in message_lower:
        top_3 = list(institutions.items())[:3]
        response = "🏆 **Top 3 Institutions by Impact**:\n\n"
        for idx, (name, data) in enumerate(top_3, 1):
            response += f"{idx}. **{name}** - Score: {data['impact_score']} ({data['sentiment']})\n"
        return response
    
    if 'positive' in message_lower or 'bullish' in message_lower:
        positive = [name for name, data in institutions.items() if data['sentiment'] == 'Positive']
        return f"📈 **Positive Sentiment Institutions**: {', '.join(positive[:5]) if positive else 'None detected'}"
    
    if 'negative' in message_lower or 'bearish' in message_lower:
        negative = [name for name, data in institutions.items() if data['sentiment'] == 'Negative']
        return f"📉 **Negative Sentiment Institutions**: {', '.join(negative[:5]) if negative else 'None detected'}"
    
    if 'india' in message_lower:
        high_india = [(name, data) for name, data in institutions.items() if data['india_linkage'] > 5]
        high_india.sort(key=lambda x: x[1]['india_linkage'], reverse=True)
        response = "🇮🇳 **High India Focus Institutions**:\n\n"
        for name, data in high_india[:5]:
            response += f"• **{name}** - {data['india_linkage']} India references\n"
        return response if high_india else "No institutions with strong India focus detected."
    
    if 'summary' in message_lower or 'overview' in message_lower:
        return "📰 **Market Summary**:\n\n" + "\n".join([f"• {s}" for s in data.get('summary', [])])
    
    # Default response
    return """I can help you with:
    
- Ask about specific institutions (e.g., "Tell me about JPMorgan")
- View top performers ("Show me the top institutions")
- Check sentiment ("Which institutions are positive/negative?")
- India focus ("Which institutions focus on India?")
- Market summary ("Give me an overview")

What would you like to know?"""

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    if news_cache['data']:
        emit('news_update', news_cache['data'])

# Scheduler for automatic updates
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=process_and_analyze_news,
    trigger="interval",
    seconds=Config.NEWS_REFRESH_INTERVAL,
    id='news_refresh',
    name='Periodic news refresh',
    replace_existing=True
)

def init_app():
    """Initialize application"""
    logger.info("Initializing Financial News Impact Analyzer...")
    logger.info(f"Environment: {Config.FLASK_ENV}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Initial data fetch
    logger.info("Performing initial news fetch...")
    process_and_analyze_news()

if __name__ == '__main__':
    try:
        init_app()
        logger.info(f"\nStarting server on {Config.HOST}:{Config.PORT}")
        socketio.run(app, 
                    host=Config.HOST, 
                    port=Config.PORT, 
                    debug=Config.DEBUG,
                    allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)