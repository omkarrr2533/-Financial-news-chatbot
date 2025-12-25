import sqlite3
import json
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='data/news_cache.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get database connection with row factory"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def init_db(self):
        """Initialize database tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # News articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT,
                    content TEXT,
                    published_date TIMESTAMP,
                    fetched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    institutions TEXT,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    india_relevance INTEGER,
                    UNIQUE(url)
                )
            ''')
            
            # Institution scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS institution_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    institution TEXT NOT NULL,
                    impact_score REAL,
                    sentiment TEXT,
                    sentiment_value REAL,
                    mentions INTEGER,
                    india_linkage INTEGER,
                    recent_articles INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performa 
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_published 
                ON articles(published_date DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_institution 
                ON institution_scores(institution, timestamp DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_url 
                ON articles(url)
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def insert_article(self, article_data):
        """Insert or update article in database"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (title, url, source, content, published_date, institutions, 
                 sentiment_score, sentiment_label, india_relevance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data.get('title', ''),
                article_data.get('url', ''),
                article_data.get('source', ''),
                article_data.get('content', ''),
                article_data.get('published_date'),
                json.dumps(article_data.get('institutions', [])),
                article_data.get('sentiment_score', 0),
                article_data.get('sentiment_label', 'Mixed'),
                article_data.get('india_relevance', 0)
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.debug(f"Article already exists: {article_data.get('url', '')}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error inserting article: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def get_recent_articles(self, hours=48):
        """Get articles from last N hours"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM articles 
                WHERE published_date >= datetime('now', '-' || ? || ' hours')
                ORDER BY published_date DESC
            ''', (hours,))
            
            articles = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Retrieved {len(articles)} articles from last {hours} hours")
            return articles
        except sqlite3.Error as e:
            logger.error(f"Error retrieving articles: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def save_institution_scores(self, scores):
        """Save institution scores in bulk"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare bulk insert data
            data = [
                (
                    institution,
                    data['impact_score'],
                    data['sentiment'],
                    data['sentiment_value'],
                    data['mentions'],
                    data['india_linkage'],
                    data['recent_articles']
                )
                for institution, data in scores.items()
            ]
            
            # Bulk insert
            cursor.executemany('''
                INSERT INTO institution_scores 
                (institution, impact_score, sentiment, sentiment_value, 
                 mentions, india_linkage, recent_articles)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data)
            
            conn.commit()
            logger.info(f"Saved {len(data)} institution scores")
        except sqlite3.Error as e:
            logger.error(f"Error saving scores: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def get_latest_scores(self, limit=10):
        """Get latest institution scores"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT institution, impact_score, sentiment, sentiment_value,
                       mentions, india_linkage, recent_articles, timestamp
                FROM institution_scores
                WHERE timestamp >= datetime('now', '-1 hour')
                ORDER BY impact_score DESC
                LIMIT ?
            ''', (limit,))
            
            scores = [dict(row) for row in cursor.fetchall()]
            return scores
        except sqlite3.Error as e:
            logger.error(f"Error retrieving scores: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def cleanup_old_data(self, days=7):
        """Clean up data older than N days"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete old articles
            cursor.execute('''
                DELETE FROM articles 
                WHERE fetched_date < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            # Delete old scores
            cursor.execute('''
                DELETE FROM institution_scores 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            conn.commit()
            logger.info(f"Cleaned up data older than {days} days")
        except sqlite3.Error as e:
            logger.error(f"Error cleaning up data: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
